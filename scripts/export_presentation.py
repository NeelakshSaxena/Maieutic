"""
Export Mentor AI Presentation to PDF and Slide Images for Visual QA
"""

import os
import win32com.client

PRESENTATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation"))
PPTX_PATH = os.path.join(PRESENTATION_DIR, "Mentor_AI_Research_Presentation.pptx")
PDF_PATH = os.path.join(PRESENTATION_DIR, "Mentor_AI_Research_Presentation.pdf")
SLIDES_DIR = os.path.join(PRESENTATION_DIR, "slides")
os.makedirs(SLIDES_DIR, exist_ok=True)

def export():
    print(f"Opening {PPTX_PATH} in PowerPoint...")
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    # Open presentation
    pres = ppt_app.Presentations.Open(PPTX_PATH, WithWindow=False)
    
    # Export to PDF (ppSaveAsPDF = 32)
    print(f"Exporting to PDF: {PDF_PATH}...")
    pres.SaveAs(PDF_PATH, 32)
    
    # Export individual slide images (1920x1080)
    slide_count = pres.Slides.Count
    print(f"Exporting {slide_count} slides to PNG...")
    slide_paths = []
    for i in range(slide_count):
        slide = pres.Slides[i]
        out_path = os.path.join(SLIDES_DIR, f"slide_{i + 1}.png")
        slide.Export(out_path, "PNG", 1920, 1080)
        slide_paths.append(out_path)
        print(f"  Exported Slide {i + 1} -> {out_path}")
        
    pres.Close()
    ppt_app.Quit()
    print("Export complete!")
    return slide_paths

if __name__ == "__main__":
    export()
