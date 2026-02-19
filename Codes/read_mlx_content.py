import matlab.engine
import os

def read_mlx_content(mlx_file_path):
    # 1. Start the MATLAB engine
    print("Starting MATLAB engine...")
    eng = matlab.engine.start_matlab()

    try:
        # Resolve absolute path for MATLAB
        abs_path = os.path.abspath(mlx_file_path)
        temp_m_file = abs_path.replace('.mlx', '_converted.m')

        # 2. Use MATLAB's 'export' function to convert MLX to plain text .m
        # Note: 'export' requires MATLAB R2022a or later
        print(f"Converting {mlx_file_path} to {temp_m_file}...")
        eng.export(abs_path, temp_m_file, nargout=0)

        # 3. Read the converted .m file content in Python
        with open(temp_m_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Optional: Clean up the temporary file
        # os.remove(temp_m_file)
        
        return content

    except Exception as e:
        return f"Error: {e}"
    finally:
        # 4. Always stop the engine to free resources
        eng.quit()

# Usage
file_path = 'your_script.mlx'
text_content = read_mlx_content(file_path)
print("--- File Content ---")
print(text_content)
