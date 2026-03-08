import os
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog

def extract_css_js_from_html(html_content: str, seperate_content: bool = False):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract CSS and JS
    css_code: list[str] | str = [] if seperate_content else ""
    js_code: list[str] | str = [] if seperate_content else ""

    # Find all style tags and extract their contents
    style_tags = soup.find_all('style')
    for tag in style_tags:
        
        if not seperate_content:
            css_code += tag.string if tag.string else ""
        else:
            css_code.append(tag.string if tag.string else "")

    # Find all script tags and extract their contents
    script_tags = soup.find_all('script')
    for tag in script_tags:
        if tag.string:  # Only extract inline scripts (ignore external sources)
            
            if not seperate_content:
                js_code += tag.string
            else:
                js_code.append(tag.string)

    # Remove style and script tags from the original HTML
    for tag in style_tags:
        tag.decompose()
    for tag in script_tags:
        tag.decompose()

    # Return the modified HTML, CSS, and JS
    new_html = str(soup)
    return new_html, css_code, js_code

def generate_link(link_template: str, amount: int) -> str:
    ret_link: str = ''
    
    if amount == 1:
            ret_link = link_template.format('')
            
    else:
        for i in range(amount):
            ret_link += link_template.format(f' ({i})')
            
    return ret_link

def write_file(code_data: list[str] | str, file_template: str, prettify: bool) -> None:
    if type(code_data) == type(str):
        with open(file_template.format(''), 'w', encoding='utf-8') as file:
            file.write(code_data)
            
    elif len(code_data) == 1:
        with open(file_template.format(''), 'w', encoding='utf-8') as file:
            file.write(code_data[0])
        
    else:
        for i in range(len(code_data)):
            with open(file_template.format(f' ({i})'), 'w', encoding='utf-8') as  file:
                file.write(code_data[i])

def save_files(new_html: str, css_code: list[str] | str, js_code: list[str] | str, prettify_html: bool, prettify_css: bool, prettify_js: bool):
    # Save the new HTML file with links to external files using UTF-8 encoding
    with open('index.html', 'w', encoding='utf-8') as html_file:
        # Update the HTML to link to external CSS and JS files
        # Don't forget about the multiple files
                
        css_link: str = generate_link('\n<link rel="stylesheet" type="text/css" href="styles{}.css">', 1 if type(css_code) == type(str) else len(css_code))
        js_link: str = generate_link('<script src="scripts{}.js"></script>\n', 1 if type(js_code) == type(str) else len(js_code))
        
        updated_html = new_html.replace(
            '<head>', 
            f'<head>{css_link}'
        ).replace(
            '</body>', 
            f'{js_link}</body>'
        )
        
        # Horrible hack, but works
        if prettify_html:
            updated_html = BeautifulSoup(updated_html, 'html.parser').prettify()
        
        html_file.write(updated_html)

    write_file(css_code, "styles{}.css", prettify_css)
    write_file(js_code, "scripts{}.js", prettify_js)

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  

    file_path = filedialog.askopenfilename(
        title="Select the HTML file",
        filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
    )

    return file_path

def display_overlay_window():
    overlay = tk.Tk()
    
    centerWidth = overlay.winfo_screenwidth() // 2 - 150
    centerHeight = overlay.winfo_screenheight() // 2 - 50
    
    overlay.title("Overlay Window")
    overlay.geometry(f"300x100+{centerWidth}+{centerHeight}")
    overlay.configure(bg='white')

    overlay.attributes("-topmost", True)
    if "transparentColor" in overlay.wm_attributes(return_python_dict=True).keys():
        overlay.attributes("-transparentcolor", 'white')  
        
    overlay.overrideredirect(True)
    
    mainFrame = tk.Frame(overlay, bg='white')
    mainFrame.pack(expand=True, anchor='center')

    upstreamLabel = tk.Label(mainFrame, text="TheZ on Top", font=('Helvetica', 24, 'bold'), fg='red', bg='white')
    upstreamLabel.pack(expand=True, anchor='n')
    
    forkLabel = tk.Label(mainFrame, text="modified by aarrbba123", font=('Helvetica', 12, 'italic'), fg='gray', bg='white')
    forkLabel.pack(expand=True, anchor='se')

    overlay.after(2000, overlay.destroy)  
    overlay.mainloop()  

def main():
    try:
        display_overlay_window()
        choice = input("Would you like to select a file using the file explorer? (y/n): ").strip().lower()

        if choice == 'y':
            file_path = open_file_dialog()
            if not file_path:
                print("No file selected, exiting...")
                return
        else:
            file_path = input("Enter the full path to the HTML file: ").strip()
            if not os.path.isfile(file_path):
                print(f"File '{file_path}' does not exist.")
                return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        
        choice = input("Would you like to seperate .JS and .CSS files (if there are multiple)? (y/n): ").strip().lower()
        
        seperate_content: bool = True if choice == 'y' else False
        
        choice = input("Would you like to prettify the output?\n(You can enter multiple values by seperating them with space, for example: css html)\n(y/css/html/js/n): ").strip().lower().split(" ")
        
        # Unintentionally pretty. (neat!)
        prettify_html: bool = True if 'html' in choice or 'y' in choice else False
        prettify_css: bool = True if 'css' in choice or 'y' in choice else False
        prettify_js: bool = True if 'js' in choice or 'y' in choice else False
        

        new_html, css_code, js_code = extract_css_js_from_html(html_content, seperate_content)
        save_files(new_html, css_code, js_code, prettify_html, prettify_css, prettify_js)

        print("Process complete: HTML, CSS, and JS have been separated and saved.")
        
    except KeyboardInterrupt:
        print("\nInterrupt recieved, exiting...")
        return

if __name__ == "__main__":
    main()
