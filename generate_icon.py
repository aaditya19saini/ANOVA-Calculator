import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io
import os

def create_icon(filename="icon.ico"):
    """
    Generates a professional-looking statistical icon (a stylized bar chart)
    and saves it as an .ico file for the Windows executable.
    """
    print(f"Generating icon: {filename}...")
    
    # Create a figure without axes
    fig, ax = plt.subplots(figsize=(2, 2), dpi=128)
    ax.axis('off')
    fig.patch.set_alpha(0.0) # Transparent background
    ax.set_facecolor((0, 0, 0, 0))
    
    # Data for a stylized bar chart (ANOVA theme)
    x = [0, 1, 2]
    heights = [3, 7, 5]
    colors = ['#f44336', '#2196F3', '#4CAF50'] # Red, Blue, Green
    
    # Draw bars
    bars = ax.bar(x, heights, color=colors, width=0.8, edgecolor='white', linewidth=2)
    
    # Add error bars to make it look like an ANOVA chart
    errors = [0.8, 1.2, 0.9]
    ax.errorbar(x, heights, yerr=errors, fmt='none', ecolor='black', capsize=8, capthick=2, elinewidth=2)
    
    # Adjust limits to fit nicely
    ax.set_xlim(-0.8, 2.8)
    ax.set_ylim(0, 9)
    
    # Save the figure to an in-memory buffer as a PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig)
    
    # Open the PNG with Pillow and save as ICO with multiple sizes
    img = Image.open(buf)
    
    # Provide multiple sizes for the ICO file for best Windows rendering
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Save the icon
    img.save(filename, format='ICO', sizes=icon_sizes)
    print(f"Successfully generated {filename}!")

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    create_icon("app_icon.ico")
