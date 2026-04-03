# Required packages
# install.packages(c("grid", "gridExtra", "gtable", "ggplot2", "cowplot", "png"))
library(grid)
library(gridExtra)
library(gtable)
library(ggplot2)
library(cowplot)
library(png)

# Constants analogous to the Python script
LEGEND_FONT_SIZE <- 7.65
LEGEND_BOX_RIGHT_OFFSET <- 0.8
BORDER_AXES_PAD <- 4.0

# Styles (approximations for grid/ggplot)
BLUE_HEX <- "#1f77b4"

# Helper: safe accessors
safe_first <- function(x, default = "") {
  if (is.null(x)) return(default)
  if (length(x) == 0) return(default)
  x[[1]]
}
coerce_text <- function(x) {
  if (is.null(x)) return("")
  as.character(x)
}

# Unit helpers
inch <- function(x) unit(x, "in")

# Table builder approximating ReportLab's make_table logic
make_table <- function(
  data,
  col_widths = NULL,                 # weights for non-empty columns (ignored for empty cols)
  available_width_in = NULL,         # width (in inches) to fit the table into
  doc = NULL,                        # if provided, uses doc$content_width as available width
  border_color = "#BFBFBF",
  header_bg = "#F2F2F2",
  body_font = list(family = "Helvetica", size = 10, face = "plain", col = "black"),
  header_font = list(family = "Helvetica", size = 10, face = "bold", col = "black"),
  # Title options
  title = NULL,                      # caption above the table (optional)
  title_font = list(family = "Helvetica", size = 11, face = "bold", col = BLUE_HEX),
  title_space_after = 4,             # space after title in points
  keep_title_with_table = TRUE
) {
  # Convert 'data' to a data.frame (character) for tableGrob
  if (is.null(data) || length(data) == 0) {
    df <- data.frame(stringsAsFactors = FALSE)
  } else {
    # Assume data is a list of rows (each a vector), convert row-wise to data.frame
    max_cols <- max(vapply(data, length, integer(1)))
    rows_norm <- lapply(data, function(r) {
      length(r) <- max_cols
      vapply(r, coerce_text, character(1))
    })
    df <- as.data.frame(do.call(rbind, rows_norm), stringsAsFactors = FALSE)
    colnames(df) <- paste0("V", seq_len(ncol(df)))
  }

  # Determine available width
  if (!is.null(doc) && is.null(available_width_in)) {
    avail_width <- doc$content_width_in
  } else if (!is.null(available_width_in)) {
    avail_width <- available_width_in
  } else {
    # Fallback if no width context is provided
    avail_width <- 6.5
  }

  # Compute column widths (in inches), similar to Python logic
  ncols <- ncol(df)
  computed_col_widths_in <- rep(NA_real_, ncols)

  # Identify empty columns: all rows empty in that column
  is_empty_cell <- function(v) {
    if (is.na(v)) return(TRUE)
    if (is.null(v)) return(TRUE)
    if (is.character(v) && trimws(v) == "") return(TRUE)
    FALSE
  }
  empty_cols <- integer(0)
  if (ncols > 0) {
    for (j in seq_len(ncols)) {
      col_vals <- df[[j]]
      col_empty <- all(vapply(col_vals, is_empty_cell, logical(1)))
      if (col_empty) empty_cols <- c(empty_cols, j)
    }
  }

  if (ncols %in% c(1, 2)) {
    first_w <- 0.215 * avail_width
    if (ncols == 1) {
      computed_col_widths_in <- c(first_w)
    } else {
      second_w <- max(avail_width - first_w, 0.0)
      computed_col_widths_in <- c(first_w, second_w)
    }
  } else if (ncols >= 3) {
    # Assign fixed width to empty columns (10% of page width each)
    empty_col_width <- if (length(empty_cols) > 0) 0.10 * avail_width else 0.0
    fixed_empty_total <- empty_col_width * length(empty_cols)

    if (fixed_empty_total > avail_width && length(empty_cols) > 0) {
      empty_col_width <- avail_width / length(empty_cols)
      fixed_empty_total <- empty_col_width * length(empty_cols)
    }

    if (length(empty_cols) > 0) {
      computed_col_widths_in[empty_cols] <- empty_col_width
    }

    remaining_width <- max(avail_width - fixed_empty_total, 0.0)
    non_empty_cols <- setdiff(seq_len(ncols), empty_cols)
    n_non_empty <- length(non_empty_cols)

    if (n_non_empty == 0) {
      if (fixed_empty_total < avail_width && length(empty_cols) > 0) {
        bump <- (avail_width - fixed_empty_total) / length(empty_cols)
        computed_col_widths_in[empty_cols] <- computed_col_widths_in[empty_cols] + bump
      }
    } else {
      weights <- NULL
      if (!is.null(col_widths) && length(col_widths) == ncols) {
        weights <- col_widths[non_empty_cols]
        total_w <- sum(weights[!is.na(weights)])
        if (!is.finite(total_w) || total_w <= 0) {
          weights <- NULL
        }
      }
      if (n_non_empty == 1) {
        computed_col_widths_in[non_empty_cols] <- remaining_width
      } else {
        if (is.null(weights)) {
          share <- remaining_width / n_non_empty
          computed_col_widths_in[non_empty_cols] <- share
        } else {
          total_w <- sum(weights)
          computed_col_widths_in[non_empty_cols] <- (weights / total_w) * remaining_width
        }
      }
    }

    # Final safety: ensure widths sum to avail_width
    missing <- which(is.na(computed_col_widths_in))
    if (length(missing) > 0) {
      remaining <- avail_width - sum(computed_col_widths_in[!is.na(computed_col_widths_in)])
      fill <- if (remaining > 0) remaining / length(missing) else 0.0
      computed_col_widths_in[missing] <- fill
    }
    total_w <- sum(computed_col_widths_in)
    if (is.finite(total_w) && total_w != 0 && abs(total_w - avail_width) > 1e-6) {
      scale <- avail_width / total_w
      computed_col_widths_in <- computed_col_widths_in * scale
    }
  }

  # Build the table grob
  tg <- tableGrob(
    df,
    rows = NULL,
    theme = ttheme_minimal(
      core = list(
        fg_params = do.call(gpar, body_font),
        padding = unit.c(unit(3, "pt"), unit(3, "pt"))
      ),
      colhead = list(
        fg_params = do.call(gpar, header_font),
        bg_params = gpar(fill = header_bg, col = NA),
        padding = unit.c(unit(6, "pt"), unit(6, "pt"))
      )
    )
  )

  # Set column widths
  if (ncol(tg) == ncols) {
    tg$widths <- unit(computed_col_widths_in, "in")
  } else {
    # tableGrob may add columns for row labels; match core columns
    core_cols <- grep("col", names(tg$widths))
    tg$widths[core_cols] <- unit(computed_col_widths_in, "in")
  }

  # Add border/grid lines similar to TableStyle (approximate)
  tg <- gtable_add_grob(
    tg,
    grobs = rectGrob(gp = gpar(col = border_color, fill = NA, lwd = 0.75)),
    t = 1, l = 1, b = nrow(tg), r = ncol(tg), name = "table-border"
  )

  # Optional title grob
  if (!is.null(title) && nzchar(title)) {
    title_grob <- textGrob(
      label = title,
      x = unit(0, "npc"),
      y = unit(1, "npc"),
      just = c("left", "top"),
      gp = gpar(
        fontfamily = title_font$family,
        fontsize = title_font$size,
        fontface = title_font$face,
        col = title_font$col
      )
    )
    spacer <- rectGrob(height = unit(title_space_after, "pt"), gp = gpar(col = NA, fill = NA))
    if (keep_title_with_table) {
      return(arrangeGrob(title_grob, spacer, tg, ncol = 1, heights = unit.c(unit(1, "grobheight", title_grob), unit(title_space_after, "pt"), unit(1, "grobheight", tg))))
    } else {
      return(list(title_grob, tg))
    }
  }

  tg
}

# Document "context" for margins and page size
make_doc_context <- function(
  pagesize_in = c(8.5, 11),        # letter size in inches (width, height)
  leftMargin_in = 0.75,
  rightMargin_in = 0.75,
  topMargin_in = 0.75,
  bottomMargin_in = 0.75,
  header_offset_in = 0.75,
  header_line_drop_in = 0.25,
  gap_below_header_line_in = 0.15
) {
  list(
    page_width_in = pagesize_in[1],
    page_height_in = pagesize_in[2],
    leftMargin_in = leftMargin_in,
    rightMargin_in = rightMargin_in,
    topMargin_in = topMargin_in,
    bottomMargin_in = bottomMargin_in,
    header_offset_in = header_offset_in,
    header_line_drop_in = header_line_drop_in,
    gap_below_header_line_in = gap_below_header_line_in,
    # derived
    content_width_in = pagesize_in[1] - leftMargin_in - rightMargin_in,
    content_height_in = pagesize_in[2] - topMargin_in - bottomMargin_in
  )
}

# Header/footer drawing (per page)
draw_header_footer <- function(doc, header_title, page_num) {
  pushViewport(viewport(width = unit(doc$page_width_in, "in"), height = unit(doc$page_height_in, "in")))
  # Header line
  y_header_line <- unit(doc$page_height_in - doc$topMargin_in - doc$header_line_drop_in, "in")
  grid.lines(
    x = unit(c(doc$leftMargin_in, doc$page_width_in - doc$rightMargin_in), "in"),
    y = unit(rep(y_header_line, 2)),
    gp = gpar(col = "black", lwd = 1)
  )
  # Header text
  grid.text(
    header_title,
    x = unit(doc$page_width_in / 2, "in"),
    y = unit(doc$page_height_in - doc$topMargin_in, "in"),
    gp = gpar(fontfamily = "Helvetica", fontsize = 9)
  )
  # Footer line
  y_footer_line <- unit(doc$bottomMargin_in + 0.5, "in")
  grid.lines(
    x = unit(c(doc$leftMargin_in, doc$page_width_in - doc$rightMargin_in), "in"),
    y = unit(rep(y_footer_line, 2)),
    gp = gpar(col = "black", lwd = 1)
  )
  # Footer page number
  grid.text(
    sprintf("Page %d", page_num),
    x = unit(doc$page_width_in / 2, "in"),
    y = unit(doc$bottomMargin_in + 0.25, "in"),
    gp = gpar(fontfamily = "Helvetica", fontsize = 9)
  )
  popViewport()
}

# Create a content viewport that respects margins and header/footer gap
push_content_viewport <- function(doc) {
  pushViewport(viewport(
    x = unit(doc$leftMargin_in, "in"),
    y = unit(doc$bottomMargin_in, "in"),
    width = unit(doc$content_width_in, "in"),
    height = unit(doc$content_height_in - doc$header_line_drop_in - doc$gap_below_header_line_in, "in"),
    just = c("left", "bottom"),
    name = "content"
  ))
}

pop_content_viewport <- function() {
  popViewport()
}

# Paragraph grob (left-aligned, blue bold)
paragraph_left_blue_bold <- function(text) {
  textGrob(
    label = text,
    x = unit(0, "npc"),
    y = unit(1, "npc"),
    just = c("left", "top"),
    gp = gpar(fontfamily = "Helvetica", fontsize = 11, fontface = "bold", col = BLUE_HEX)
  )
}

spacer_grob_in <- function(h_in) {
  rectGrob(height = unit(h_in, "in"), gp = gpar(col = NA, fill = NA))
}

# Unit helpers for scalar/units (simplified)
get_unit <- function(vehData, setIdx, key) {
  sd <- vehData[[setIdx]][["scalarData"]]
  sd_units <- vehData[[setIdx]][["scalarDataUnits"]]
  if (is.list(sd_units) && !is.null(sd_units[[key]])) return(as.character(sd_units[[key]]))
  units_dict <- if (is.list(sd)) sd[["Units"]] else NULL
  if (is.list(units_dict) && !is.null(units_dict[[key]])) return(as.character(units_dict[[key]]))
  ""
}
get_unit_scalar_bin <- function(vehData, setIdx, key) {
  sbd <- vehData[[setIdx]][["scalarBinData"]]
  sbd_units <- vehData[[setIdx]][["scalarBinDataUnits"]]
  if (is.list(sbd_units) && !is.null(sbd_units[[key]])) return(as.character(sbd_units[[key]]))
  units_dict <- if (is.list(sbd)) sbd[["Units"]] else NULL
  if (is.list(units_dict) && !is.null(units_dict[[key]])) return(as.character(units_dict[[key]]))
  ""
}

# Header table builder
header_table <- function(logData, veh_model, filename, doc) {
  data <- list(
    c("Date and Time", safe_first(logData[["dateTime"]])),
    c("Vehicle Model", veh_model),
    c("Vehicle ID", safe_first(logData[["vehicleID"]])),
    c("File Name", filename)
  )
  make_table(data = data, doc = doc)
}

# Figure helpers (simplified ggplot2-based versions)
figure_included_intervals <- function(setIdx, vehData, udp, logData) {
  img_path <- "include_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    Include_EngSpeed = vehData[["Include_EngSpeed"]],
    EngineRPM = vehData[["EngineRPM"]],
    Include_Regen = vehData[["Include_Regen"]],
    DPFRegenStatus = vehData[["DPFRegenStatus"]],
    Include_Tmax = vehData[["Include_Tmax"]],
    TMax_ExcludeLimit = vehData[["TMax_ExcludeLimit"]],
    LimitAdjustediSCB_LAT = vehData[["LimitAdjustediSCB_LAT"]],
    Include_Ambient5C = vehData[["Include_Ambient5C"]],
    AmbientT_ExcludeLimit = vehData[["AmbientT_ExcludeLimit"]],
    Include_Altitude = vehData[["Include_Altitude"]],
    Altitude_ExcludeLimit = vehData[["Altitude_ExcludeLimit"]],
    Altitude_Ft = vehData[["Altitude_Ft"]],
    Include_Total = vehData[["Include_Total"]]
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_EngSpeed), color = "blue", linewidth = 0.6) +
    labs(y = "Include Engine", x = NULL) +
    theme_minimal(base_size = 9) +
    theme(panel.grid.major.x = element_blank())

  p2 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_Regen), color = "blue", linewidth = 0.6) +
    labs(y = "Include Regen", x = NULL) +
    theme_minimal(base_size = 9) +
    theme(panel.grid.major.x = element_blank())

  p3 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_Tmax), color = "blue", linewidth = 0.6) +
    geom_line(aes(y = TMax_ExcludeLimit), color = "brown", linewidth = 0.6) +
    geom_line(aes(y = LimitAdjustediSCB_LAT), color = "darkgreen", linewidth = 0.6) +
    labs(y = "Include TMax", x = NULL) +
    theme_minimal(base_size = 9) +
    theme(panel.grid.major.x = element_blank())

  p4 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_Ambient5C), color = "blue", linewidth = 0.6) +
    geom_line(aes(y = AmbientT_ExcludeLimit), color = "brown", linewidth = 0.6) +
    geom_line(aes(y = LimitAdjustediSCB_LAT), color = "darkgreen", linewidth = 0.6) +
    labs(y = "Include AmbT 5C", x = NULL) +
    theme_minimal(base_size = 9) +
    theme(panel.grid.major.x = element_blank())

  p5 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_Altitude), color = "blue", linewidth = 0.6) +
    geom_line(aes(y = Altitude_ExcludeLimit), color = "brown", linewidth = 0.6) +
    geom_line(aes(y = Altitude_Ft), color = "darkgreen", linewidth = 0.6) +
    labs(y = "Include Altitude", x = NULL) +
    theme_minimal(base_size = 9) +
    theme(panel.grid.major.x = element_blank())

  p6 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = Include_Total), color = "blue", linewidth = 0.6) +
    labs(y = "Include Total", x = "Time (s)") +
    theme_minimal(base_size = 9)

  g <- plot_grid(p1, p2, p3, p4, p5, p6, ncol = 1, rel_heights = c(1,1,1,1,1,1))
  ggsave(img_path, g, width = 7.75, height = 7.75, dpi = 150, units = "in")
  img_path
}

figure_invalid_intervals <- function(setIdx, vehData, udp, binData, logData, binData_avg) {
  img_path <- "incTotal_image.png"
  df0 <- data.frame(TIME = vehData[["TIME"]], Include_Total = vehData[["Include_Total"]])
  df1 <- data.frame(Time_BinAvg = binData_avg[["Time_BinAvg"]], Invalid_Intervals = binData_avg[["Invalid_Intervals"]])

  p1 <- ggplot(df0, aes(x = TIME, y = Include_Total)) +
    geom_line(color = "blue", linewidth = 1) +
    labs(y = "Include Total", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df1, aes(x = Time_BinAvg, y = Invalid_Intervals)) +
    geom_line(color = "black", linewidth = 0.8) +
    labs(y = "Invalid Intervals", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, ncol = 1, rel_heights = c(1, 1))
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

figure_bin1_nox <- function(setIdx, vehData, udp, binData, logData) {
  img_path <- "bin1Nox_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    VehicleSpeedMPH = vehData[["VehicleSpeedMPH"]],
    EngineRPM = vehData[["EngineRPM"]],
    kNOx_MassFlow = vehData[["kNOx_MassFlow"]]
  )
  dfb <- data.frame(
    Time_BinAvg = as.numeric(binData[["Time_BinAvg"]]),
    NOx_Mass_Bin1 = as.numeric(binData[["NOx_Mass_Bin1"]]),
    NOxMassFlow_Bin1_Cummulative = as.numeric(binData[["NOxMassFlow_Bin1_Cummulative"]])
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = VehicleSpeedMPH), color = "blue") +
    labs(y = "Vehicle Speed (mph)", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df, aes(x = TIME, y = kNOx_MassFlow)) +
    geom_line(color = "#1a3352") +
    labs(y = "kNOx Mass Flow (g/hr)", x = NULL) +
    theme_minimal(base_size = 10)

  p3 <- ggplot(dfb, aes(x = Time_BinAvg)) +
    geom_line(aes(y = NOx_Mass_Bin1), color = "#346599") +
    geom_line(aes(y = NOxMassFlow_Bin1_Cummulative), color = "#803333") +
    labs(y = "NOx Mass / Cumulative (gm / gm/hr)", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, p3, ncol = 1)
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

figure_norm_co2 <- function(setIdx, vehData, udp, binData, logData, binData_avg) {
  img_path <- "normCO2_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    VehicleSpeedMPH = vehData[["VehicleSpeedMPH"]],
    EngineRPM = vehData[["EngineRPM"]],
    CO2_MassFlow = vehData[["CO2_MassFlow"]]
  )
  dfb <- data.frame(
    Time_BinAvg = binData_avg[["Time_BinAvg"]],
    mCO2_Norm = binData_avg[["mCO2_Norm"]],
    BIN = binData_avg[["BIN"]]
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = EngineRPM), color = "#8c563b") +
    geom_line(aes(y = VehicleSpeedMPH), color = "blue") +
    labs(y = "Speed/RPM", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df, aes(x = TIME, y = CO2_MassFlow)) +
    geom_line(color = "#334f99") +
    labs(y = "CO2 Mass Flow (g/hr)", x = NULL) +
    theme_minimal(base_size = 10)

  p3 <- ggplot(dfb, aes(x = Time_BinAvg)) +
    geom_line(aes(y = mCO2_Norm), color = "#7e2f8e") +
    geom_hline(yintercept = 6, color = "#d25519", linewidth = 1) +
    geom_line(aes(y = BIN), color = "#77ab43") +
    labs(y = "Normalized CO2 (%) / Bin", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, p3, ncol = 1)
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

figure_bin2_nox <- function(setIdx, vehData, udp, binData, logData) {
  img_path <- "bin2NOx_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    VehicleSpeedMPH = vehData[["VehicleSpeedMPH"]],
    EngineRPM = vehData[["EngineRPM"]],
    kNOx_MassFlow = vehData[["kNOx_MassFlow"]]
  )
  dfb <- data.frame(
    Time_BinAvg = binData[["Time_BinAvg"]],
    NOx_Mass_Bin2 = binData[["NOx_Mass_Bin2"]],
    NOx_BrakeSpec_Bin2_Cummulative = binData[["NOx_BrakeSpec_Bin2_Cummulative"]]
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = VehicleSpeedMPH), color = "blue") +
    labs(y = "Vehicle Speed (mph)", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df, aes(x = TIME, y = kNOx_MassFlow)) +
    geom_line(color = "#1a3352") +
    labs(y = "kNOx Mass Flow (g/hr)", x = NULL) +
    theme_minimal(base_size = 10)

  p3 <- ggplot(dfb, aes(x = Time_BinAvg)) +
    geom_line(aes(y = NOx_Mass_Bin2), color = "#346599") +
    geom_line(aes(y = NOx_BrakeSpec_Bin2_Cummulative), color = "#803333") +
    labs(y = "NOx Mass / BS Cum", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, p3, ncol = 1)
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

figure_bin2_co <- function(setIdx, vehData, udp, binData, logData) {
  img_path <- "bin2CO_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    VehicleSpeedMPH = vehData[["VehicleSpeedMPH"]],
    EngineRPM = vehData[["EngineRPM"]],
    CO_MassFlow = vehData[["CO_MassFlow"]]
  )
  dfb <- data.frame(
    Time_BinAvg = binData[["Time_BinAvg"]],
    CO_Mass_Bin2 = binData[["CO_Mass_Bin2"]],
    CO_BrakeSpec_Bin2_Cummulative = binData[["CO_BrakeSpec_Bin2_Cummulative"]]
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = VehicleSpeedMPH), color = "blue") +
    labs(y = "Vehicle Speed (mph)", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df, aes(x = TIME, y = CO_MassFlow)) +
    geom_line(color = "#1a3352") +
    labs(y = "CO Mass Flow (g/hr)", x = NULL) +
    theme_minimal(base_size = 10)

  p3 <- ggplot(dfb, aes(x = Time_BinAvg)) +
    geom_line(aes(y = CO_Mass_Bin2), color = "#346599") +
    geom_line(aes(y = CO_BrakeSpec_Bin2_Cummulative), color = "#803333") +
    labs(y = "CO Mass / BS Cum", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, p3, ncol = 1)
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

figure_bin2_hc <- function(setIdx, vehData, udp, binData, logData, binData_avg) {
  img_path <- "bin2HC_image.png"
  df <- data.frame(
    TIME = vehData[["TIME"]],
    VehicleSpeedMPH = vehData[["VehicleSpeedMPH"]],
    EngineRPM = vehData[["EngineRPM"]],
    HC_MassFlow = vehData[["HC_MassFlow"]]
  )
  dfb <- data.frame(
    Time_BinAvg = binData[["Time_BinAvg"]],
    HC_Mass_Bin2 = binData[["HC_Mass_Bin2"]],
    HC_BrakeSpec_Bin2_Cummulative = binData[["HC_BrakeSpec_Bin2_Cummulative"]]
  )

  p1 <- ggplot(df, aes(x = TIME)) +
    geom_line(aes(y = VehicleSpeedMPH), color = "blue") +
    labs(y = "Vehicle Speed (mph)", x = NULL) +
    theme_minimal(base_size = 10)

  p2 <- ggplot(df, aes(x = TIME, y = HC_MassFlow)) +
    geom_line(color = "#1a3352") +
    labs(y = "HC Mass Flow (g/hr)", x = NULL) +
    theme_minimal(base_size = 10)

  p3 <- ggplot(dfb, aes(x = Time_BinAvg)) +
    geom_line(aes(y = HC_Mass_Bin2), color = "#346599") +
    geom_line(aes(y = HC_BrakeSpec_Bin2_Cummulative), color = "#803333") +
    labs(y = "HC Mass / BS Cum", x = "Time (s)") +
    theme_minimal(base_size = 10)

  g <- plot_grid(p1, p2, p3, ncol = 1)
  ggsave(img_path, g, width = 7.5, height = 8.0, dpi = 150, units = "in")
  img_path
}

# Main report function (R translation of Python reportPEMS_HDOffcycleBins)
reportPEMS_HDOffcycleBins <- function(
  setIdx,
  filename,
  vehData,
  udp,
  scalarData,
  scalarBinData,
  logData,
  binData,
  binData_avg
) {
  # Full PDF path
  file_path <- "C:/Users/slee02/Matlab/RoadaC"  # Adjust as needed
  pdf_path <- file.path(file_path, paste0(filename, ".pdf"))

  # Header title and model string
  oem <- safe_first(logData[["oem"]])
  model <- safe_first(logData[["model"]])
  my <- safe_first(logData[["my"]])

  header_title <- sprintf("NVFEL Laboratory:  PEMS Test Report:  %s %s %s", oem, model, my)
  veh_model <- sprintf("%s %s %s", oem, model, my)

  # Document context (margins and sizes)
  doc <- make_doc_context(
    pagesize_in = c(8.5, 11),
    leftMargin_in = 0.75,
    rightMargin_in = 0.75,
    topMargin_in = 0.75,
    bottomMargin_in = 0.75,
    header_offset_in = 0.75,
    header_line_drop_in = 0.25,
    gap_below_header_line_in = 0.15
  )

  # Open PDF device
  pdf(pdf_path, width = doc$page_width_in, height = doc$page_height_in)
  on.exit(dev.off(), add = TRUE)

  page_num <- 1
  grid.newpage()
  draw_header_footer(doc, header_title, page_num)
  push_content_viewport(doc)

  # PAGE 1 - Test Information
  # Spacer below header
  s1 <- spacer_grob_in(0.25)

  # Test Information
  title1 <- paragraph_left_blue_bold("Test Information")
  pg1_tab1_data <- list(
    c("Date and Time", safe_first(logData[["dateTime"]])),
    c("Vehicle Model", veh_model),
    c("Vehicle ID", safe_first(logData[["vehicleID"]])),
    c("File Name", filename)
  )
  tbl1 <- make_table(pg1_tab1_data, doc = doc)

  # Vehicle and Cycle
  title2 <- paragraph_left_blue_bold("Vehicle and Cycle")
  dist_val <- safe_first(scalarData[["Distance_Mile"]], "")
  dist_unit <- "miles"
  dist_str <- if (is.numeric(dist_val)) sprintf("%10.2f %s", dist_val, dist_unit) else as.character(dist_val)

  test_cycle <- safe_first(logData[["testCycle"]])
  odo <- safe_first(logData[["odo"]])
  fuel <- safe_first(logData[["fuel"]])
  vin <- safe_first(logData[["vin"]])
  notes <- safe_first(logData[["notes"]])

  pg1_tab2_data <- list(
    c("Test Cycle", test_cycle, "       ", "Fuel", fuel),
    c("Cycle Distance", dist_str, "       ", "VIN", vin),
    c("Odometer", odo, "       ", "Notes", notes)
  )
  tbl2 <- make_table(pg1_tab2_data, doc = doc)

  # Test Cycle Mass Emissions
  title3 <- paragraph_left_blue_bold("Test Cycle Mass Emissions")
  scalar_with_unit <- function(key) {
    val <- safe_first(scalarData[[key]])
    unit <- "g/mile"
    val_str <- if (is.numeric(val)) sprintf("%8.4f", val) else as.character(val)
    list(unit = unit, val = val_str)
  }
  nox <- scalar_with_unit("kNOx_Gms_Per_Mile")
  co <- scalar_with_unit("CO_Gms_Per_Mile")
  hc <- scalar_with_unit("HC_Gms_Per_Mile")
  co2 <- scalar_with_unit("CO2_Gms_Per_Mile")

  pg1_tab3_render <- list(
    c("NOx", "CO", "HC", "CO2"),
    c(nox$unit, co$unit, hc$unit, co2$unit),
    c(nox$val, co$val, hc$val, co2$val)
  )
  tbl3 <- make_table(pg1_tab3_render, doc = doc)

  # Particulate Emissions
  title4 <- paragraph_left_blue_bold("Particulate Emissions")
  pg1_tab4_data <- list(
    c("Filter Number", "Pre-Weight", "Post-Weight", "Net Total Mass", "Total Mass/Dis"),
    c("(-)", "(mg)", "(mg)", "(mg)", "(gm/mile)"),
    c(" ", " ", " ", " ", " ")
  )
  tbl4 <- make_table(pg1_tab4_data, doc = doc)

  # Fuel Economy
  title5 <- paragraph_left_blue_bold("Fuel Economy")
  fe_val <- safe_first(scalarData[["Fuel_Economy"]], "")
  fe_unit <- "mpg"
  fe_val_str <- if (is.numeric(fe_val)) sprintf("%8.2f", fe_val) else as.character(fe_val)
  pg1_tab5_data <- list(c("Fuel Economy"), c(fe_unit), c(fe_val_str))
  tbl5 <- make_table(pg1_tab5_data, doc = doc)

  # Off-Cycle Emissions - Intervals
  title6 <- paragraph_left_blue_bold("Off-Cycle Emissions - Intervals")
  sb <- scalarBinData
  pg1_tab6_data <- list(
    c("Total Intervals", "Valid Intervals", "Invalid Intervals", "Bin 1 Intervals", "Bin 2 Intervals"),
    c(
      safe_first(sb[["Number_Intervals"]]),
      safe_first(sb[["NumValid_Intervals"]]),
      safe_first(sb[["NumInValid_Intervals"]]),
      safe_first(sb[["NumBin1_Intervals"]]),
      safe_first(sb[["NumBin2_Intervals"]])
    )
  )
  tbl6 <- make_table(pg1_tab6_data, doc = doc)

  # Bin 1 NOx Emissions
  title7 <- paragraph_left_blue_bold("Bin 1 NOx Emissions")
  bin1_nox_val <- safe_first(scalarBinData[["NOxMassFlow_Bin1"]], "")
  bin1_nox_unit <- "g/hr"
  bin1_nox_val_str <- if (is.numeric(bin1_nox_val)) sprintf("%8.4f", bin1_nox_val) else as.character(bin1_nox_val)
  pg1_tab7_data <- list(c("NOx Bin 1"), c(bin1_nox_unit), c(bin1_nox_val_str))
  tbl7 <- make_table(pg1_tab7_data, doc = doc)

  # Bin 2 NOx Emissions
  title8 <- paragraph_left_blue_bold("Bin 2 NOx Emissions")
  bin2_nox_val <- safe_first(scalarBinData[["NOxBrakeSpecific_Bin2"]], "")
  bin2_hc_val <- safe_first(scalarBinData[["hcBrakeSpecific_Bin2"]], "")
  bin2_co_val <- safe_first(scalarBinData[["coBrakeSpecific_Bin2"]], "")
  pg1_tab8_render <- list(
    c("NOx Bin 2", "HC Bin 2", "PM Bin 2", "CO Bin 2"),
    c("mg/hp-hr", "mg/hp-hr", "--", "g/hp-hr"),
    c(
      if (is.numeric(bin2_nox_val)) sprintf("%8.4f", bin2_nox_val) else as.character(bin2_nox_val),
      if (is.numeric(bin2_hc_val)) sprintf("%8.4f", bin2_hc_val) else as.character(bin2_hc_val),
      "--",
      if (is.numeric(bin2_co_val)) sprintf("%8.4f", bin2_co_val) else as.character(bin2_co_val)
    )
  )
  tbl8 <- make_table(pg1_tab8_render, doc = doc)

  # Arrange and draw Page 1 content
  page1 <- arrangeGrob(
    s1,
    title1, tbl1,
    title2, tbl2,
    title3, tbl3,
    title4, tbl4,
    title5, tbl5,
    title6, tbl6,
    title7, tbl7,
    title8, tbl8,
    ncol = 1
  )
  grid.draw(page1)
  pop_content_viewport()

  # Page 2: Included Intervals
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  title_info <- paragraph_left_blue_bold("Test Information")
  grid.draw(title_info)
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Included Intervals"))
  include_image_path <- figure_included_intervals(setIdx, vehData, udp, logData)
  img <- readPNG(include_image_path)
  grid.raster(img, width = inch(7.75), height = inch(7.75), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 3: Invalid Intervals
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Invalid Intervals"))
  invalid_image_path <- figure_invalid_intervals(setIdx, vehData, udp, binData, logData, binData_avg)
  img <- readPNG(invalid_image_path)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 4: Bin 1 NOx
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Bin 1 NOx"))
  p <- figure_bin1_nox(setIdx, vehData, udp, binData, logData)
  img <- readPNG(p)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 5: Normalized CO2
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Normalized CO2"))
  p <- figure_norm_co2(setIdx, vehData, udp, binData, logData, binData_avg)
  img <- readPNG(p)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 6: Bin 2 NOx
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Bin 2 NOx"))
  p <- figure_bin2_nox(setIdx, vehData, udp, binData, logData)
  img <- readPNG(p)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 7: Bin 2 CO
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Bin 2 CO"))
  p <- figure_bin2_co(setIdx, vehData, udp, binData, logData)
  img <- readPNG(p)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Page 8: Bin 2 HC
  page_num <- page_num + 1
  grid.newpage(); draw_header_footer(doc, header_title, page_num); push_content_viewport(doc)
  grid.draw(paragraph_left_blue_bold("Test Information"))
  grid.draw(header_table(logData, veh_model, filename, doc))
  grid.draw(paragraph_left_blue_bold("Figure:  Bin 2 HC"))
  p <- figure_bin2_hc(setIdx, vehData, udp, binData, logData, binData_avg)
  img <- readPNG(p)
  grid.raster(img, width = inch(7.5), height = inch(8.0), x = unit(0, "npc"), y = unit(0, "npc"), just = c("left", "bottom"))
  pop_content_viewport()

  # Close device via on.exit
  pdf_path
}