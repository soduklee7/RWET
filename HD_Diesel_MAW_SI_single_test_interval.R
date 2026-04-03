# EPA MAW Emissions Analysis and Shift-Day Emissions (R version)
# Conversion of the provided Python script to R.
#
# Required packages:
# - readxl
# - dplyr
# - stringr
# - ggplot2
# - openxlsx
# - pdftools
# - caTools
# - gridExtra
#
# Install any missing packages:
# install.packages(c("readxl", "dplyr", "stringr", "ggplot2", "openxlsx", "pdftools", "caTools", "gridExtra"))

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(stringr)
  library(ggplot2)
  library(openxlsx)
  library(pdftools)
  library(caTools)
  library(gridExtra)
})

# ---------------------------
# Helper utilities
# ---------------------------

to_numeric <- function(col) {
  # Convert a column-like to numeric vector, preserving length.
  if (is.null(col)) return(NULL)
  # Handle factors/characters robustly
  suppressWarnings(as.numeric(as.character(col)))
}

normalize_colname <- function(name) {
  tolower(trimws(as.character(name)))
}

get_column <- function(df, candidates) {
  # Return the first matching column by exact name (case-insensitive) among candidates.
  # If none found, returns NULL.
  if (is.null(df) || NROW(df) == 0) return(NULL)
  names_norm <- vapply(names(df), normalize_colname, FUN.VALUE = character(1))
  for (c in candidates) {
    c_norm <- normalize_colname(c)
    idx <- which(names_norm == c_norm)
    if (length(idx) > 0) {
      return(df[[idx[1]]])
    }
  }
  return(NULL)
}

find_col_contains <- function(df, must_have_substrings) {
  # Return first column whose name contains all provided substrings (case-insensitive).
  # Returns vector or NULL.
  if (is.null(df) || length(names(df)) == 0) return(NULL)
  subs <- vapply(must_have_substrings, normalize_colname, FUN.VALUE = character(1))
  for (col in names(df)) {
    lc <- normalize_colname(col)
    if (all(vapply(subs, function(s) grepl(s, lc, fixed = TRUE), logical(1)))) {
      return(df[[col]])
    }
  }
  return(NULL)
}

grams_to_gallons <- function(mass_g, fuel_or_density = NULL) {
  # Convert fuel mass (grams) to US gallons.
  # fuel_or_density can be:
  #   - numeric: density in kg/L
  #   - string: 'gasoline','e10','e85','diesel'
  # Default gasoline E0 (0.745 kg/L).
  rho <- 0.745
  if (is.null(fuel_or_density)) {
    rho <- 0.745
  } else if (is.numeric(fuel_or_density)) {
    rho <- as.numeric(fuel_or_density)
  } else {
    kind <- tolower(trimws(as.character(fuel_or_density)))
    rho <- switch(kind,
      "gasoline" = 0.745,
      "petrol"   = 0.745,
      "e0"       = 0.745,
      "e10"      = 0.750,
      "e85"      = 0.785,
      "diesel"   = 0.832,
      "d2"       = 0.832,
      stop("Unknown fuel type. Provide density (kg/L) or a known fuel string.")
    )
  }
  liters <- (as.numeric(mass_g) / 1000.0) / rho
  gallons <- liters / 3.785411784
  return(gallons)
}

# ---------------------------
# Core calculations (Diesel MAW)
# ---------------------------

calculate_maw_and_subintervals <- function(df, eCO2_g_hp_hr, pmax_hp) {
  # Implements the MAW windowing, exclusions, binning, and summary.
  # Returns: list(df=df, summary_df=summary_df, windows_df=windows_df, sub_interval_df=sub_summary, invalid_count=invalid_count)

  # Base engine calcs
  df$EnginePower_hp <- (df$Engine_Torque_Nm * df$Engine_RPM) / 7120.8
  df$Altitude_ft <- df$Altitude_m * 3.28084
  df$Distance_mi <- df$v_mph / 3600.0

  # Exclusion logic
  tmax_c <- (-0.0014 * df$Altitude_ft) + 37.78
  excluded <- (
    (df$AmbTempC < -5.0) |
      (df$AmbTempC > tmax_c) |
      (df$Altitude_ft > 5500.0) |
      (df$Engine_RPM < 1.0) |
      (if ("In_Regen" %in% names(df)) as.logical(df$In_Regen) else FALSE)
  )
  excluded[is.na(excluded)] <- TRUE

  # Re-classify isolated valid points as excluded (valid flanked by excluded)
  shift_fwd <- c(TRUE, excluded[-length(excluded)])
  shift_bwd <- c(excluded[-1], TRUE)
  isolated_valid <- shift_fwd & shift_bwd & (!excluded)
  excluded[isolated_valid] <- TRUE
  df$Excluded_Data <- excluded

  # Sub-Interval IDs based on excluded breaks
  df$Sub_Interval_ID <- cumsum(as.integer(df$Excluded_Data))

  # Valid-only dataframe subset, also record original indices
  valid_idx <- which(!df$Excluded_Data)
  if (length(valid_idx) == 0) {
    sub_summary <- data.frame()
    return(list(df = df, summary_df = data.frame(), windows_df = data.frame(), sub_interval_df = sub_summary, invalid_count = 0))
  }

  valid_df <- df[valid_idx, , drop = FALSE]
  valid_df$Original_Time_Sec <- valid_idx

  # Sub-interval summary
  sub_summary <- valid_df %>%
    group_by(Sub_Interval_ID) %>%
    summarise(
      Duration_sec   = n(),
      Avg_Power_hp   = mean(EnginePower_hp, na.rm = TRUE),
      Work_hp_hr     = sum(EnginePower_hp, na.rm = TRUE) / 3600.0,
      Distance_mi    = sum(Distance_mi, na.rm = TRUE),
      NOx_g          = sum(instNOx, na.rm = TRUE),
      PM_g           = sum(instPM, na.rm = TRUE),
      HC_g           = sum(instHC, na.rm = TRUE),
      CO_g           = sum(instCO, na.rm = TRUE),
      CO2_g          = sum(instCO2, na.rm = TRUE),
      .groups = "drop"
    )

  # MAW windows
  total_points <- nrow(df)
  num_valid <- length(valid_idx)
  if (num_valid < 300) {
    return(list(df = df, summary_df = data.frame(), windows_df = data.frame(), sub_interval_df = sub_summary, invalid_count = 0))
  }

  # Mapping from chrono index -> valid order index (1..num_valid), 0 for excluded
  chrono_to_valid <- integer(total_points)
  chrono_to_valid[] <- 0L
  chrono_to_valid[valid_idx] <- seq_len(num_valid)

  # Prealloc containers
  windows <- list(
    Window_Index = integer(0),
    Window_Start_Time = integer(0),
    Window_End_Time = integer(0),
    Excluded_Samples_Count = integer(0),
    Total_Work_hp_hr = numeric(0),
    Total_Distance_mi = numeric(0),
    Total_Fuelrate_g = numeric(0),
    eCO2norm_percent = numeric(0),
    Bin = integer(0),
    massNOx = numeric(0),
    massHC = numeric(0),
    massPM = numeric(0),
    massCO = numeric(0),
    massCO2 = numeric(0),
    NOx_mg_mi = numeric(0),
    HC_mg_mi = numeric(0),
    PM_mg_mi = numeric(0),
    CO_g_mi = numeric(0),
    CO2_g_mi = numeric(0)
  )

  bin2_denom <- eCO2_g_hp_hr * pmax_hp * (300.0 / 3600.0)
  invalid_count <- 0L

  trapezoid_col <- function(s) {
    a <- to_numeric(s)
    a[is.na(a)] <- 0.0
    # trapezoid with dx = 1.0
    caTools::trapz(x = seq_along(a), y = a)
  }

  for (i in seq(1, total_points - 1L)) {
    # require window starts with two consecutive valid points
    if (excluded[i] || excluded[i + 1L]) next

    v_start <- chrono_to_valid[i]
    if (v_start <= 0L) next
    if ((v_start + 299L) > num_valid) break

    # 300th valid's chrono index
    j <- valid_idx[v_start + 299L]
    valid_end <- FALSE
    valid_samples_count <- 300L

    # Ensure window end is also preceded by a valid (j-1)
    if (!excluded[j - 1L]) {
      valid_end <- TRUE
    } else {
      if ((v_start + 300L) <= num_valid) {
        j_301 <- valid_idx[v_start + 300L]
        if (!excluded[j_301 - 1L]) {
          j <- j_301
          valid_end <- TRUE
          valid_samples_count <- 301L
        }
      }
    }

    if (valid_end) {
      window_full <- df[i:j, , drop = FALSE]
      win_valid <- window_full[!window_full$Excluded_Data, , drop = FALSE]

      time_start <- i
      time_end <- j
      excluded_count <- sum(window_full$Excluded_Data, na.rm = TRUE)

      t_CO2 <- trapezoid_col(win_valid$instCO2)
      t_NOx <- trapezoid_col(win_valid$instNOx)
      t_PM  <- trapezoid_col(win_valid$instPM)
      t_HC  <- trapezoid_col(win_valid$instHC)
      t_CO  <- trapezoid_col(win_valid$instCO)
      t_work <- trapezoid_col(win_valid$EnginePower_hp) / 3600.0
      t_dist <- trapezoid_col(win_valid$Distance_mi)
      t_fuelrate <- trapezoid_col(win_valid$instFuelRate)

      eCO2norm_pct <- if (bin2_denom > 0) (t_CO2 / bin2_denom) * 100.0 else NA_real_

      if (t_dist > 0) {
        n_mi <- (t_NOx * 1000.0) / t_dist
        h_mi <- (t_HC  * 1000.0) / t_dist
        p_mi <- (t_PM  * 1000.0) / t_dist
        c_mi <- t_CO  / t_dist
        c2_mi <- t_CO2 / t_dist
      } else {
        n_mi <- h_mi <- p_mi <- c_mi <- c2_mi <- NA_real_
      }

      if (excluded_count > 599L) {
        # Invalid window
        bin_label <- 0L
        invalid_count <- invalid_count + 1L

        windows$Window_Index <- c(windows$Window_Index, i)
        windows$Window_Start_Time <- c(windows$Window_Start_Time, time_start)
        windows$Window_End_Time <- c(windows$Window_End_Time, time_end)
        windows$Excluded_Samples_Count <- c(windows$Excluded_Samples_Count, excluded_count)
        windows$Total_Work_hp_hr <- c(windows$Total_Work_hp_hr, NA_real_)
        windows$Total_Distance_mi <- c(windows$Total_Distance_mi, NA_real_)
        windows$Total_Fuelrate_g <- c(windows$Total_Fuelrate_g, NA_real_)
        windows$eCO2norm_percent <- c(windows$eCO2norm_percent, NA_real_)
        windows$Bin <- c(windows$Bin, bin_label)
        windows$massNOx <- c(windows$massNOx, NA_real_)
        windows$massHC  <- c(windows$massHC, NA_real_)
        windows$massPM  <- c(windows$massPM, NA_real_)
        windows$massCO  <- c(windows$massCO, NA_real_)
        windows$massCO2 <- c(windows$massCO2, NA_real_)
        windows$NOx_mg_mi <- c(windows$NOx_mg_mi, NA_real_)
        windows$HC_mg_mi  <- c(windows$HC_mg_mi, NA_real_)
        windows$PM_mg_mi  <- c(windows$PM_mg_mi, NA_real_)
        windows$CO_g_mi   <- c(windows$CO_g_mi, NA_real_)
        windows$CO2_g_mi  <- c(windows$CO2_g_mi, NA_real_)
      } else {
        # Valid window
        bin_label <- if (!is.na(eCO2norm_pct) && eCO2norm_pct < 6.0) 1L else 2L

        windows$Window_Index <- c(windows$Window_Index, i)
        windows$Window_Start_Time <- c(windows$Window_Start_Time, time_start)
        windows$Window_End_Time <- c(windows$Window_End_Time, time_end)
        windows$Excluded_Samples_Count <- c(windows$Excluded_Samples_Count, excluded_count)
        windows$Total_Work_hp_hr <- c(windows$Total_Work_hp_hr, t_work)
        windows$Total_Distance_mi <- c(windows$Total_Distance_mi, t_dist)
        windows$Total_Fuelrate_g <- c(windows$Total_Fuelrate_g, t_fuelrate)
        windows$eCO2norm_percent <- c(windows$eCO2norm_percent, eCO2norm_pct)
        windows$Bin <- c(windows$Bin, bin_label)
        windows$massNOx <- c(windows$massNOx, t_NOx)
        windows$massHC  <- c(windows$massHC,  t_HC)
        windows$massPM  <- c(windows$massPM,  t_PM)
        windows$massCO  <- c(windows$massCO,  t_CO)
        windows$massCO2 <- c(windows$massCO2, t_CO2)
        windows$NOx_mg_mi <- c(windows$NOx_mg_mi, n_mi)
        windows$HC_mg_mi  <- c(windows$HC_mg_mi,  h_mi)
        windows$PM_mg_mi  <- c(windows$PM_mg_mi,  p_mi)
        windows$CO_g_mi   <- c(windows$CO_g_mi,   c_mi)
        windows$CO2_g_mi  <- c(windows$CO2_g_mi,  c2_mi)
      }
    }
  }

  if (length(windows$Window_Index) == 0L) {
    return(list(df = df, summary_df = data.frame(), windows_df = data.frame(), sub_interval_df = sub_summary, invalid_count = invalid_count))
  }

  windows_df <- as.data.frame(windows)

  valid_wins <- windows_df %>% filter(Bin != 0L)
  if (nrow(valid_wins) == 0L) {
    return(list(df = df, summary_df = data.frame(), windows_df = windows_df, sub_interval_df = sub_summary, invalid_count = invalid_count))
  }

  # Summary by bin
  summary_base <- valid_wins %>%
    group_by(Bin) %>%
    summarise(
      Total_Windows = n(),
      Avg_eCO2norm_Percent = mean(eCO2norm_percent, na.rm = TRUE),
      .groups = "drop"
    )

  # Overall distance-based NOx mg/mi using the entire DF (including excluded)
  total_dist <- sum(df$Distance_mi, na.rm = TRUE)
  overall_nox_mg_mi <- if (total_dist > 0) (sum(df$instNOx, na.rm = TRUE) * 1000.0) / total_dist else NA_real_

  # Bin-specific metrics
  summary_df <- summary_base
  summary_df$Avg_Bin1_NOx_g_hr <- NA_real_
  summary_df$Avg_Bin2_NOx_mg_hp_hr <- NA_real_
  summary_df$Avg_Bin2_HC_mg_hp_hr <- NA_real_
  summary_df$Avg_Bin2_PM_mg_hp_hr <- NA_real_
  summary_df$Avg_Bin2_CO_g_hp_hr <- NA_real_
  summary_df$Avg_Bin2_CO2_g_hp_hr <- NA_real_
  summary_df$Avg_NOx_mg_mi <- overall_nox_mg_mi

  # Bin 1
  if (any(summary_df$Bin == 1L)) {
    mask_bin1 <- valid_wins$Bin == 1L
    num_bin1 <- sum(mask_bin1)
    if (num_bin1 > 0) {
      nox_bin1 <- (sum(valid_wins$massNOx[mask_bin1], na.rm = TRUE) / (300.0 * num_bin1)) * 3600.0
      summary_df$Avg_Bin1_NOx_g_hr[summary_df$Bin == 1L] <- nox_bin1
    }
  }

  # Bin 2
  if (any(summary_df$Bin == 2L)) {
    mask_bin2 <- valid_wins$Bin == 2L
    sumCO2_Bin2 <- sum(valid_wins$massCO2[mask_bin2], na.rm = TRUE)
    if (sumCO2_Bin2 > 0) {
      n2 <- (sum(valid_wins$massNOx[mask_bin2], na.rm = TRUE) / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0
      c2 <- (sum(valid_wins$massCO[mask_bin2], na.rm = TRUE) / sumCO2_Bin2) * eCO2_g_hp_hr
      h2 <- (sum(valid_wins$massHC[mask_bin2], na.rm = TRUE) / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0
      p2 <- (sum(valid_wins$massPM[mask_bin2], na.rm = TRUE) / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0

      summary_df$Avg_Bin2_NOx_mg_hp_hr[summary_df$Bin == 2L] <- n2
      summary_df$Avg_Bin2_CO_g_hp_hr[summary_df$Bin == 2L] <- c2
      summary_df$Avg_Bin2_HC_mg_hp_hr[summary_df$Bin == 2L] <- h2
      summary_df$Avg_Bin2_PM_mg_hp_hr[summary_df$Bin == 2L] <- p2
      summary_df$Avg_Bin2_CO2_g_hp_hr[summary_df$Bin == 2L] <- eCO2_g_hp_hr
    }
  }

  # Standards vs Test Values
  Tamb <- mean(df$AmbTempC, na.rm = TRUE)
  if (!is.na(Tamb) && Tamb < 25) {
    NOxBin1Std <- 10.4 + ((25 - Tamb) * 0.25)
    NOxBin2Std <- 63 + ((25 - Tamb) * 2.2)
  } else {
    NOxBin1Std <- 10.4
    NOxBin2Std <- 63.0
  }

  val_bin1 <- summary_df$Avg_Bin1_NOx_g_hr[summary_df$Bin == 1L]
  val_bin2 <- summary_df$Avg_Bin2_NOx_mg_hp_hr[summary_df$Bin == 2L]
  NOxBin1 <- if (length(val_bin1) > 0) as.numeric(val_bin1[1]) else NA_real_
  NOxBin2 <- if (length(val_bin2) > 0) as.numeric(val_bin2[1]) else NA_real_

  message("Standards vs Test Values")
  message(sprintf("Bin1 NOx: Standard %.1f g/hr | Test %s g/hr", NOxBin1Std, if (!is.na(NOxBin1)) sprintf("%.4f", NOxBin1) else "NA"))
  message(sprintf("Bin2 NOx: Standard %.0f mg/hp*hr | Test %s mg/hp*hr", round(NOxBin2Std), if (!is.na(NOxBin2)) sprintf("%.3f", NOxBin2) else "NA"))

  return(list(df = df, summary_df = summary_df, windows_df = windows_df, sub_interval_df = sub_summary, invalid_count = invalid_count))
}

evaluate_compliance <- function(summary_df, limits) {
  # Build a compliance table comparing bin averages against regulatory limits.
  # limits: list with keys:
  #   Bin1_NOx_g_hr, Bin2_NOx_mg_hp_hr, Bin2_HC_mg_hp_hr, Bin2_PM_mg_hp_hr, Bin2_CO_g_hp_hr, Bin2_CO2_g_hp_hr
  if (is.null(summary_df) || nrow(summary_df) == 0L) {
    return(data.frame(Bin = integer(0), Metric = character(0), Actual_Average = numeric(0), Regulatory_Limit = numeric(0), Status = character(0)))
  }

  rows <- list()

  for (i in seq_len(nrow(summary_df))) {
    b <- as.integer(summary_df$Bin[i])
    if (b == 1L) {
      actual <- summary_df$Avg_Bin1_NOx_g_hr[i]
      limit <- limits[["Bin1_NOx_g_hr"]]
      status <- if (!is.na(actual) && actual <= limit) "PASS" else "FAIL"
      rows[[length(rows) + 1L]] <- data.frame(Bin = 1L, Metric = "NOx (g/hr)", Actual_Average = round(as.numeric(actual), 3), Regulatory_Limit = limit, Status = status)
    } else if (b == 2L) {
      mets <- list(
        list(label = "NOx (mg/hp-hr)", col = "Avg_Bin2_NOx_mg_hp_hr", limkey = "Bin2_NOx_mg_hp_hr"),
        list(label = "HC (mg/hp-hr)",  col = "Avg_Bin2_HC_mg_hp_hr",  limkey = "Bin2_HC_mg_hp_hr"),
        list(label = "PM (mg/hp-hr)",  col = "Avg_Bin2_PM_mg_hp_hr",  limkey = "Bin2_PM_mg_hp_hr"),
        list(label = "CO (g/hp-hr)",   col = "Avg_Bin2_CO_g_hp_hr",   limkey = "Bin2_CO_g_hp_hr"),
        list(label = "CO2 (g/hp-hr)",  col = "Avg_Bin2_CO2_g_hp_hr",  limkey = "Bin2_CO2_g_hp_hr")
      )
      for (m in mets) {
        actual <- summary_df[[m$col]][i]
        limit <- limits[[m$limkey]]
        status <- if (!is.na(actual) && actual <= limit) "PASS" else "FAIL"
        rows[[length(rows) + 1L]] <- data.frame(Bin = 2L, Metric = m$label, Actual_Average = round(as.numeric(actual), 3), Regulatory_Limit = limit, Status = status)
      }
    }
  }

  do.call(rbind, rows)
}

# ---------------------------
# Plotting for Diesel MAW
# ---------------------------

compute_excluded_intervals <- function(excl_vec) {
  # Given logical vector of excluded flags, returns a data.frame of start/end intervals (1-based, inclusive)
  x <- as.integer(excl_vec)
  diff_excl <- diff(c(0L, x, 0L))
  starts <- which(diff_excl == 1L)
  ends <- which(diff_excl == -1L) - 1L
  data.frame(xmin = starts, xmax = ends)
}

plot_shift_day_emissions <- function(df, pdf_file = NULL) {
  time_sec <- nrow(df)
  t <- seq_len(time_sec)

  excl_df <- compute_excluded_intervals(df$Excluded_Data)

  # Tile 1: Engine Power + excluded patches
  p1 <- ggplot() +
    geom_line(aes(x = t, y = df$EnginePower_hp), color = "#0072BD", linewidth = 0.8) +
    geom_rect(data = excl_df, aes(xmin = xmin - 0.5, xmax = xmax + 0.5, ymin = -Inf, ymax = Inf),
              fill = "red", alpha = 0.2, inherit.aes = FALSE) +
    labs(title = "Engine Test Data: Valid vs. Excluded Regions", y = "Engine Power (hp)", x = NULL) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))

  # Tile 2: v_mph (left) and instCO2 (right) via two y-axes (approximation using scaling)
  # We'll use two separate geoms with secondary axis using ggplot2's sec.axis
  # Scale instCO2 to align roughly with v_mph for visualization only.
  vmph <- df$v_mph
  co2 <- df$instCO2
  scale_factor <- max(vmph, na.rm = TRUE) / max(co2, na.rm = TRUE)
  co2_scaled <- co2 * scale_factor

  p2 <- ggplot() +
    geom_line(aes(x = t, y = vmph, color = "Vehicle Speed (mph)"), linewidth = 0.8) +
    geom_line(aes(x = t, y = co2_scaled, color = "Instantaneous CO2 (g/s)"), linewidth = 0.7) +
    geom_rect(data = excl_df, aes(xmin = xmin - 0.5, xmax = xmax + 0.5, ymin = -Inf, ymax = Inf),
              fill = "red", alpha = 0.2, inherit.aes = FALSE) +
    scale_color_manual(values = c("Vehicle Speed (mph)" = "#77AC30", "Instantaneous CO2 (g/s)" = "#D95319")) +
    scale_y_continuous(name = "Vehicle Speed (mph)",
                       sec.axis = sec_axis(~ . / scale_factor, name = "Instantaneous CO2 (g/s)")) +
    labs(x = "Time (seconds)", color = NULL) +
    theme_minimal() +
    theme(legend.position = "top")

  if (!is.null(pdf_file)) {
    grDevices::pdf(pdf_file, width = 10, height = 6)
    print(p1)
    print(p2)
    grDevices::dev.off()
  } else {
    gridExtra::grid.arrange(p1, p2, nrow = 2)
  }
}

plot_cumulative_emissions <- function(df, eCO2_g_hp_hr, pdf_file = NULL) {
  valid_df <- df[!df$Excluded_Data, , drop = FALSE]
  if (nrow(valid_df) == 0L) {
    message("No valid data available for cumulative plots.")
    return(invisible(NULL))
  }

  valid_df$Cum_NOx_g <- cumsum(replace(valid_df$instNOx, is.na(valid_df$instNOx), 0.0))
  valid_df$Cum_CO2_g <- cumsum(replace(valid_df$instCO2, is.na(valid_df$instCO2), 0.0))
  valid_df$Cum_Work_hp_hr <- cumsum(replace(valid_df$EnginePower_hp, is.na(valid_df$EnginePower_hp), 0.0) / 3600.0)

  bs_nox <- rep(0.0, nrow(valid_df))
  work_pos <- valid_df$Cum_Work_hp_hr > 0
  bs_nox[work_pos] <- valid_df$Cum_NOx_g[work_pos] / valid_df$Cum_Work_hp_hr[work_pos]
  valid_df$BS_NOx_g_hp_hr <- bs_nox

  c2 <- valid_df$Cum_CO2_g
  c2[c2 == 0] <- NA_real_
  valid_df$bs_nox_eCO2 <- (valid_df$Cum_NOx_g / c2) * eCO2_g_hp_hr

  t_valid <- seq_len(nrow(valid_df))

  p1 <- ggplot(valid_df, aes(x = t_valid)) +
    geom_line(aes(y = Cum_NOx_g, color = "Cumulative NOx (g)"), linewidth = 0.9) +
    geom_line(aes(y = Cum_CO2_g, color = "Cumulative CO2 (g)"), linewidth = 0.9, linetype = "dashed") +
    scale_color_manual(values = c("Cumulative NOx (g)" = "#A2142F", "Cumulative CO2 (g)" = "#7E2F8E")) +
    labs(title = "Cumulative Emissions Accrual During Valid Testing", y = "Mass (g)", x = NULL, color = NULL) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))

  final_avg <- NA_real_
  if (any(!is.na(valid_df$BS_NOx_g_hp_hr))) {
    final_avg <- tail(na.omit(valid_df$BS_NOx_g_hp_hr), 1)
  }

  p2 <- ggplot(valid_df, aes(x = t_valid)) +
    geom_line(aes(y = BS_NOx_g_hp_hr, color = "BS NOx via Work (g/hp-hr)"), linewidth = 0.9) +
    geom_line(aes(y = bs_nox_eCO2, color = "BS NOx via eCO2 (g/hp-hr)"), linewidth = 0.9) +
    scale_color_manual(values = c("BS NOx via Work (g/hp-hr)" = "#0072BD", "BS NOx via eCO2 (g/hp-hr)" = "#77AC30")) +
    labs(x = "Time (Original Second of Shift)", y = "Cum. BS NOx (g/hp-hr)", color = NULL) +
    theme_minimal()
  if (!is.na(final_avg)) {
    p2 <- p2 + geom_hline(yintercept = final_avg, linetype = "dotted", color = "black") +
      annotate("text", x = max(t_valid, na.rm = TRUE), y = final_avg, hjust = 1, vjust = -0.2,
               label = sprintf("Final Avg: %.3f g/hp-hr", final_avg), size = 3)
  }

  # Save or display
  if (!is.null(pdf_file)) {
    # Append pages to existing PDF by creating a temporary PDF and combining
    tmp_pdf <- tempfile(fileext = ".pdf")
    grDevices::pdf(tmp_pdf, width = 10, height = 6)
    print(p1)
    print(p2)
    grDevices::dev.off()
    append_fig_to_pdf(pdf_file, tmp_pdf)
    unlink(tmp_pdf)
  } else {
    gridExtra::grid.arrange(p1, p2, nrow = 2)
  }
}

# ---------------------------
# Shift-Day (Gasoline) calculations
# ---------------------------

calculate_shift_day_emissions <- function(df, ftp_eco2_g_hp_hr, pmax_hp) {
  # Shift-day emissions using both Work method and Pmax/eCO2 method.
  # Returns: list(df=df, results=results, sub_summary=sub_summary)

  df$EnginePower_hp <- (df$Engine_Torque_Nm * df$Engine_RPM) / 7120.8
  df$Altitude_ft <- df$Altitude_m * 3.28084
  df$Distance_mi <- df$v_mph / 3600.0

  # Total mass from ALL data (including excluded)
  total_distance_mi <- sum(df$Distance_mi, na.rm = TRUE)
  total_all_NOx_g <- sum(df$instNOx, na.rm = TRUE)
  total_all_PM_g  <- sum(df$instPM,  na.rm = TRUE)
  total_all_HC_g  <- sum(df$instHC,  na.rm = TRUE)
  total_all_CO_g  <- sum(df$instCO,  na.rm = TRUE)
  total_all_CO2_g <- sum(df$instCO2, na.rm = TRUE)

  # Exclusions
  tmax_c <- (-0.0014 * df$Altitude_ft) + 37.78
  excluded <- (
    (df$AmbTempC < -5.0) |
      (df$AmbTempC > tmax_c) |
      (df$Altitude_ft > 5500.0) |
      (df$Engine_RPM < 1.0) |
      (if ("In_Regen" %in% names(df)) as.logical(df$In_Regen) else FALSE)
  )
  excluded[is.na(excluded)] <- TRUE
  df$Excluded_Data <- excluded
  df$Sub_Interval_ID <- cumsum(as.integer(df$Excluded_Data))

  valid_df <- df[!df$Excluded_Data, , drop = FALSE]
  if (nrow(valid_df) == 0L) stop("Error: No valid data points found.")

  # Sub-interval summary
  sub_summary <- valid_df %>%
    group_by(Sub_Interval_ID) %>%
    summarise(
      Duration_sec   = n(),
      Avg_Power_hp   = mean(EnginePower_hp, na.rm = TRUE),
      Work_hp_hr     = sum(EnginePower_hp, na.rm = TRUE) / 3600.0,
      Distance_mi    = sum(Distance_mi, na.rm = TRUE),
      NOx_g          = sum(instNOx, na.rm = TRUE),
      PM_g           = sum(instPM, na.rm = TRUE),
      HC_g           = sum(instHC, na.rm = TRUE),
      CO_g           = sum(instCO, na.rm = TRUE),
      CO2_g          = sum(instCO2, na.rm = TRUE),
      .groups = "drop"
    )

  total_valid_NOx_g <- sum(valid_df$instNOx, na.rm = TRUE)
  total_valid_PM_g  <- sum(valid_df$instPM,  na.rm = TRUE)
  total_valid_HC_g  <- sum(valid_df$instHC,  na.rm = TRUE)
  total_valid_CO_g  <- sum(valid_df$instCO,  na.rm = TRUE)
  total_valid_CO2_g <- sum(valid_df$instCO2, na.rm = TRUE)
  total_work_hp_hr  <- sum(valid_df$EnginePower_hp, na.rm = TRUE) / 3600.0
  valid_distance_mi <- sum(valid_df$Distance_mi, na.rm = TRUE)

  bs_multiplier_work <- if (total_work_hp_hr > 0) 1.0 / total_work_hp_hr else NA_real_

  results <- list()
  results[["Total_Shift_Seconds"]] <- as.integer(nrow(df))
  results[["Total_Valid_Seconds"]] <- as.integer(nrow(valid_df))
  results[["Total_Excluded_Seconds"]] <- as.integer(sum(df$Excluded_Data, na.rm = TRUE))
  results[["Total_Sub_Intervals_Stitched"]] <- as.integer(dplyr::n_distinct(valid_df$Sub_Interval_ID))
  results[["Total_Work_hp_hr"]] <- as.numeric(total_work_hp_hr)
  results[["Total_Distance_mi"]] <- as.numeric(total_distance_mi)
  results[["Valid_Distance_mi"]] <- as.numeric(valid_distance_mi)

  # Work method - VALID ONLY
  results[["NOx_mg_hp_hr_Work"]] <- if (!is.na(bs_multiplier_work)) as.numeric((total_valid_NOx_g * 1000.0) * bs_multiplier_work) else NA_real_
  results[["PM_mg_hp_hr_Work"]]  <- if (!is.na(bs_multiplier_work)) as.numeric((total_valid_PM_g  * 1000.0) * bs_multiplier_work) else NA_real_
  results[["HC_mg_hp_hr_Work"]]  <- if (!is.na(bs_multiplier_work)) as.numeric((total_valid_HC_g  * 1000.0) * bs_multiplier_work) else NA_real_
  results[["CO_g_hp_hr_Work"]]   <- if (!is.na(bs_multiplier_work)) as.numeric(total_valid_CO_g * bs_multiplier_work) else NA_real_
  results[["CO2_g_hp_hr_Work"]]  <- if (!is.na(bs_multiplier_work)) as.numeric(total_valid_CO2_g * bs_multiplier_work) else NA_real_

  # Pmax/eCO2 method - VALID ONLY
  if (total_valid_CO2_g > 0) {
    ratio <- ftp_eco2_g_hp_hr / total_valid_CO2_g
    results[["NOx_mg_Pmax_eCO2"]] <- as.numeric(total_valid_NOx_g * 1000.0 * ratio)
    results[["PM_mg_Pmax_eCO2"]]  <- as.numeric(total_valid_PM_g  * 1000.0 * ratio)
    results[["HC_mg_Pmax_eCO2"]]  <- as.numeric(total_valid_HC_g  * 1000.0 * ratio)
    results[["CO_g_Pmax_eCO2"]]   <- as.numeric(total_valid_CO_g * ratio)
    results[["CO2_g_Pmax_eCO2"]]  <- as.numeric(ftp_eco2_g_hp_hr)
  } else {
    results[["NOx_mg_Pmax_eCO2"]] <- NA_real_
    results[["PM_mg_Pmax_eCO2"]]  <- NA_real_
    results[["HC_mg_Pmax_eCO2"]]  <- NA_real_
    results[["CO_g_Pmax_eCO2"]]   <- NA_real_
    results[["CO2_g_Pmax_eCO2"]]  <- as.numeric(ftp_eco2_g_hp_hr)
  }

  # Distance-specific (total, using ALL data)
  if (total_distance_mi > 0) {
    results[["NOx_mg_mi_TotalDist"]] <- as.numeric((total_all_NOx_g * 1000.0) / total_distance_mi)
    results[["PM_mg_mi_TotalDist"]]  <- as.numeric((total_all_PM_g  * 1000.0) / total_distance_mi)
    results[["HC_mg_mi_TotalDist"]]  <- as.numeric((total_all_HC_g  * 1000.0) / total_distance_mi)
    results[["CO_g_mi_TotalDist"]]   <- as.numeric(total_all_CO_g / total_distance_mi)
    results[["CO2_g_mi_TotalDist"]]  <- as.numeric(total_all_CO2_g / total_distance_mi)
  } else {
    results[["NOx_mg_mi_TotalDist"]] <- NA_real_
    results[["PM_mg_mi_TotalDist"]]  <- NA_real_
    results[["HC_mg_mi_TotalDist"]]  <- NA_real_
    results[["CO_g_mi_TotalDist"]]   <- NA_real_
    results[["CO2_g_mi_TotalDist"]]  <- NA_real_
  }

  # Distance-specific (valid only)
  if (valid_distance_mi > 0) {
    results[["NOx_mg_mi_ValidDist"]] <- as.numeric((total_valid_NOx_g * 1000.0) / valid_distance_mi)
    results[["PM_mg_mi_ValidDist"]]  <- as.numeric((total_valid_PM_g  * 1000.0) / valid_distance_mi)
    results[["HC_mg_mi_ValidDist"]]  <- as.numeric((total_valid_HC_g  * 1000.0) / valid_distance_mi)
    results[["CO_g_mi_ValidDist"]]   <- as.numeric(total_valid_CO_g / valid_distance_mi)
    results[["CO2_g_mi_ValidDist"]]  <- as.numeric(total_valid_CO2_g / valid_distance_mi)
  } else {
    results[["NOx_mg_mi_ValidDist"]] <- NA_real_
    results[["PM_mg_mi_ValidDist"]]  <- NA_real_
    results[["HC_mg_mi_ValidDist"]]  <- NA_real_
    results[["CO_g_mi_ValidDist"]]   <- NA_real_
    results[["CO2_g_mi_ValidDist"]]  <- NA_real_
  }

  return(list(df = df, results = results, sub_summary = sub_summary))
}

# ---------------------------
# PDF helpers
# ---------------------------

save_two_pages <- function(pdf_file, plot1, plot2, width = 10, height = 6, dpi = 300) {
  grDevices::pdf(pdf_file, width = width, height = height)
  print(plot1)
  print(plot2)
  grDevices::dev.off()
}

append_fig_to_pdf <- function(pdf_file, new_pdf_path) {
  # Append pages from new_pdf_path to an existing PDF, or create it if it doesn't exist.
  pdf_file <- normalizePath(pdf_file, mustWork = FALSE)
  new_pdf_path <- normalizePath(new_pdf_path, mustWork = TRUE)

  if (!file.exists(pdf_file)) {
    # Create by copying
    file.copy(new_pdf_path, pdf_file, overwrite = TRUE)
    message(sprintf("Created: %s", pdf_file))
    return(invisible(TRUE))
  }

  # Combine existing with new
  tmp_out <- tempfile(fileext = ".pdf")
  pdftools::pdf_combine(c(pdf_file, new_pdf_path), output = tmp_out)
  file.rename(tmp_out, pdf_file)
  message(sprintf("Appended page to: %s", pdf_file))
  invisible(TRUE)
}

# ---------------------------
# Main orchestration
# ---------------------------

run_emissions_analysis <- function(excelfile, binData_avg, raw = NULL, udp = NULL, MPG = NULL, fuel_density = NULL, do_plots = TRUE) {
  # Build base df from raw table and run either Diesel MAW or Gasoline shift-day logic.
  # Returns: list(df=df, results=results)

  # Read sheets
  raw_df         <- readxl::read_excel(excelfile, sheet = "vehData_data")
  udp_bins_df    <- readxl::read_excel(excelfile, sheet = "udp_bins")
  udp_log_df     <- readxl::read_excel(excelfile, sheet = "udp_log")
  udp_fuel_df    <- readxl::read_excel(excelfile, sheet = "udp_fuel")
  udp_scalar_df  <- readxl::read_excel(excelfile, sheet = "scalar")
  scalarBinData  <- readxl::read_excel(excelfile, sheet = "scalarBinData")
  logData        <- readxl::read_excel(excelfile, sheet = "logData")
  binData        <- readxl::read_excel(excelfile, sheet = "binData")

  udp <- list(
    bins = list(
      eco2fcl = udp_bins_df$eco2fcl,
      pmax    = udp_bins_df$pmax
    ),
    log = list(
      fuel = udp_log_df$fuel
    ),
    fuel = list(
      fuel_sg = udp_fuel_df$sg
    ),
    scalar = list(
      MPG = udp_scalar_df$Fuel_Economy
    )
  )

  # Flexible name handling to find key columns:
  # Ambient temp column (try "LimitAdjusted..._LAT" or "Temp_Amb")
  amb_col_series <- find_col_contains(raw_df, c("limitadjusted", "_lat"))
  if (is.null(amb_col_series)) amb_col_series <- get_column(raw_df, c("Temp_Amb"))
  # Vehicle speed column
  veh_spd_series <- find_col_contains(raw_df, c("vehicle", "speed"))
  # Instantaneous fuel flow (g/s)
  inst_fuel_series <- get_column(raw_df, c("InstantaneousFuelFlow", "Instantaneous Fuel Flow"))

  # Build df with key signals (robust fallbacks if missing)
  df <- data.frame(stringsAsFactors = FALSE)
  df$Time        <- to_numeric(get_column(raw_df, c("TIME")))
  df$AmbTempC    <- to_numeric(amb_col_series %||% get_column(raw_df, c("Temp_Amb")))

  # Emission massflow signals (g/s); adapt to your dataset names
  df$instCO      <- to_numeric(get_column(raw_df, c("CO_MassFlow", "CO_Mass_Sec")))
  df$instCO2     <- to_numeric(get_column(raw_df, c("CO2_MassFlow", "CO2_Mass_Sec")))

  pm_series <- get_column(raw_df, c("PM_Mass_Sec_Final", "PM_Mass_sec_Final", "PM_Mass_Sec", "PM_Mass_sec"))
  df$instPM      <- if (is.null(pm_series)) rep(0.0, nrow(df)) else to_numeric(pm_series)

  df$instHC      <- to_numeric(get_column(raw_df, c("HC_MassFlow", "THC_Mass_Sec")))
  df$instNOx     <- to_numeric(get_column(raw_df, c("kNOx_MassFlow", "NOX_Mass_sec_Final", "NOX_Mass_Sec", "NOX_Mass_sec")))
  regen_series   <- get_column(raw_df, c("DPFRegenStatus", "Regen"))
  df$In_Regen    <- if (!is.null(regen_series)) to_numeric(regen_series) else rep(0.0, nrow(raw_df))

  alt_ft_series  <- to_numeric(get_column(raw_df, c("Altitude_Ft", "Alt")))
  df$Altitude_m  <- if (!is.null(alt_ft_series) && any(!is.na(alt_ft_series))) alt_ft_series / 3.28084 else rep(0.0, nrow(raw_df))

  df$Engine_RPM          <- to_numeric(get_column(raw_df, c("EngineRPM")))
  df$Engine_Torque_Nm    <- to_numeric(get_column(raw_df, c("DerivedEngineTorque")))
  df$Engine_Torque_lb_ft <- to_numeric(get_column(raw_df, c("DerivedEngineTorque_1")))

  df$Distance <- to_numeric(get_column(raw_df, c("Cumulative_Distance_Miles", "Distance")))

  v_series <- veh_spd_series %||% get_column(raw_df, c("Vehicle Speed", "VehicleSpeedMPH", "Veh_Speed"))
  df$v_mph <- to_numeric(v_series)

  df$instFuelRate <- to_numeric(inst_fuel_series)

  # Replace fully-missing columns with zeros to avoid NA propagation in sums
  for (c in c("instCO", "instCO2", "instPM", "instHC", "instNOx", "Engine_RPM", "Engine_Torque_Nm", "v_mph", "instFuelRate")) {
    if (c %in% names(df)) {
      df[[c]][is.na(df[[c]])] <- 0.0
    }
  }

  # Extract configuration values
  eCO2_g_hp_hr <- as.numeric(udp$bins$eco2fcl[1])
  pmax_hp      <- as.numeric(udp$bins$pmax[1])
  fuel_type    <- as.character(udp$log$fuel[1])
  fuel_density <- as.numeric(udp$fuel$fuel_sg[1])
  MPG          <- as.numeric(udp$scalar$MPG[1])

  results <- list()

  if (identical(fuel_type, "Diesel")) {
    res <- calculate_maw_and_subintervals(df, eCO2_g_hp_hr, pmax_hp)
    df <- res$df
    summary_df <- res$summary_df
    windows_df <- res$windows_df
    sub_interval_df <- res$sub_interval_df
    invalid_count <- res$invalid_count

    if (!is.null(summary_df) && nrow(summary_df) > 0L) {
      message(sprintf("Total Invalid Windows (>599s Excluded): %d", invalid_count))
      epa_limits <- list(
        Bin1_NOx_g_hr       = 10.4,
        Bin2_NOx_mg_hp_hr   = 63.0,
        Bin2_HC_mg_hp_hr    = 130.0,
        Bin2_PM_mg_hp_hr    = 5.0,
        Bin2_CO_g_hp_hr     = 9.25,
        Bin2_CO2_g_hp_hr    = 600.0
      )
      compliance_df <- evaluate_compliance(summary_df, epa_limits)
      message("--- EPA MAW Compliance Report ---")
      print(compliance_df)

      results[["summary_df"]]      <- summary_df
      results[["windows_df"]]      <- windows_df
      results[["sub_interval_df"]] <- sub_interval_df
      results[["compliance_df"]]   <- compliance_df

      excel_file <- normalizePath("MAW_outputs.xlsx", mustWork = FALSE)
      if (file.exists(excel_file)) unlink(excel_file)

      wb <- openxlsx::createWorkbook()
      openxlsx::addWorksheet(wb, "maw_detailed_windows");  openxlsx::writeData(wb, "maw_detailed_windows", windows_df)
      openxlsx::addWorksheet(wb, "maw_summary_averages");  openxlsx::writeData(wb, "maw_summary_averages", summary_df)
      openxlsx::addWorksheet(wb, "maw_compliance_report"); openxlsx::writeData(wb, "maw_compliance_report", compliance_df)
      openxlsx::addWorksheet(wb, "sub_intervals_summary"); openxlsx::writeData(wb, "sub_intervals_summary", sub_interval_df)
      openxlsx::saveWorkbook(wb, excel_file, overwrite = TRUE)
      message(sprintf("Excel workbook written: %s", excel_file))
    } else {
      message("Error: No valid MAW data could be generated.")
      results[["summary_df"]]      <- data.frame()
      results[["windows_df"]]      <- data.frame()
      results[["sub_interval_df"]] <- data.frame()
      results[["compliance_df"]]   <- data.frame()
    }

    if (isTRUE(do_plots)) {
      message("Generating visual analytics...")
      pdf_file <- "shift_day_cumulative_emissions.pdf"
      plot_shift_day_emissions(df, pdf_file = pdf_file)
      plot_cumulative_emissions(df, eCO2_g_hp_hr, pdf_file = pdf_file)
    }
  } else if (identical(fuel_type, "Gasoline")) {
    res <- calculate_shift_day_emissions(df, eCO2_g_hp_hr, pmax_hp)
    df <- res$df
    final_emissions <- res$results
    sub_interval_df <- res$sub_summary

    # Simple data quality log
    total_sec    <- final_emissions[["Total_Shift_Seconds"]]
    valid_sec    <- final_emissions[["Total_Valid_Seconds"]]
    excluded_sec <- final_emissions[["Total_Excluded_Seconds"]]
    message("--- Data Quality & Exclusion Summary ---")
    message(sprintf("Total Shift Duration : %d seconds", total_sec))
    message(sprintf("Valid Data Points    : %d seconds (%.1f%%)", valid_sec, (valid_sec / total_sec) * 100.0))
    message(sprintf("Excluded Data Points : %d seconds (%.1f%%)", excluded_sec, (excluded_sec / total_sec) * 100.0))

    results[["final_emissions"]] <- final_emissions
    results[["sub_interval_df"]] <- sub_interval_df
  } else {
    stop("Unknown fuel type. Expected 'Diesel' or 'Gasoline'.")
  }

  # Optionally compute MPG estimate if given density and distances
  if (!is.null(fuel_density)) {
    gals <- sum(grams_to_gallons(replace(df$instFuelRate, is.na(df$instFuelRate), 0.0), fuel_density))
    if (gals > 0) {
      MPG_est <- sum(replace(df$v_mph, is.na(df$v_mph), 0.0)) / 3600.0 / gals
      message(sprintf("MPG @ pems    : %s , MPG_est %.2f", if (!is.null(MPG) && !is.na(MPG)) sprintf("%.2f", MPG) else "NA", MPG_est))
    }
  }

  # Placeholder for reportPEMS_HDOffcycleBins equivalent in R (not implemented)
  # setIdx <- 1
  # vehData <- raw_df
  # reportPEMS_HDOffcycleBins(setIdx, sub("_udp.*$", "", excelfile), vehData, udp, udp_scalar_df, scalarBinData, logData, binData, binData_avg)

  return(list(df = df, results = results))
}

# Utility infix for NULL coalescing
`%||%` <- function(a, b) if (!is.null(a)) a else b

# ---------------------------
# Example usage
# ---------------------------

# Wrap in tryCatch for safety
tryCatch({
  # Update paths as needed
  excelfile <- "C:/Users/slee02/Matlab/RoadaC/pp_2021_Volvo_VNL_White_HWY_20240429_M1-M97_udp.xlsx"
  binData_avg <- tryCatch(read.csv("C:/Users/slee02/Matlab/RoadaC/pp_2021_Volvo_VNL_White_HWY_20240429_M1-M97_binData.csv"), error = function(e) data.frame())

  res <- run_emissions_analysis(
    excelfile = excelfile,
    binData_avg = binData_avg,
    raw = NULL,
    udp = NULL,
    MPG = NULL,
    fuel_density = 0.832,
    do_plots = TRUE
  )

  df <- res$df
  results <- res$results

  cat("\n=== Analysis Complete ===\n")
  cat(sprintf("DataFrame shape: %d rows, %d cols\n", nrow(df), ncol(df)))
  cat(sprintf("\nResults keys: %s\n", paste(names(results), collapse = ", ")))
}, error = function(e) {
  message(sprintf("Error during analysis: %s", e$message))
  print(e)
})