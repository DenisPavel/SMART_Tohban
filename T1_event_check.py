import os
import glob
import time
import webbrowser
import pathlib

#import numpy as np
#import matplotlib.pyplot as pl


def create_image_sequence_html(image_dir, output_html='image_sequence.html', delay_ms=100):
    """
    Generates an HTML file with JavaScript to animate an image sequence.
    """
    # Find all image files with common extensions and sort them numerically
    extensions = ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp')
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(image_dir, ext)))
    
    # Sort files naturally (e.g., file_1.jpg before file_10.jpg)
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

    if not files:
        print(f"No images found in {image_dir}")
        return

    # Check if we should save inside the image dir to keep links relative (recommended for portability)
    html_dir = os.path.dirname(output_html)
    if not html_dir:
         output_html = os.path.join(image_dir, output_html)
         html_dir = image_dir

    num_frames = len(files)
    
    # Generate relative paths for portability (works on GitHub, other computers)
    try:
        files_js = [os.path.relpath(f, html_dir).replace(os.sep, '/') for f in files]
    except ValueError:
        # Fallback to absolute URIs if relative paths are impossible (e.g. different drives on Windows)
        files_js = [pathlib.Path(f).absolute().as_uri() for f in files]

    file_names = [os.path.basename(f) for f in files]
    
    # JavaScript to handle animation
    js_script = f"""
    var aniFrames = new Array({num_frames});
    var imageFiles = {files_js};
    var imageNames = {file_names};
    var frameNum = 0;
    var maxFrameNum = {num_frames} - 1;
    var timeout_id = null;
    var delay = {delay_ms}; // Milliseconds

    function showFrame() {{
        document.imageWindow.src = aniFrames[frameNum].src;
        // Update frame number display
        var counter = document.getElementById('frameCounter');
        if (counter) counter.innerHTML = (frameNum + 1) + '/' + {num_frames};
    }}

    function animate() {{
        frameNum++;
        if (frameNum > maxFrameNum) frameNum = 0; // Loop animation
        showFrame();
        timeout_id = setTimeout(animate, delay);
    }}

    function startAnimate() {{
        if (timeout_id) return; // Already running
        animate();
    }}

    function killAnimate(){{
        if (timeout_id) clearTimeout(timeout_id);
        timeout_id = null;
    }}

    function stepNext() {{
        killAnimate();
        frameNum++;
        if (frameNum > maxFrameNum) frameNum = 0;
        showFrame();
    }}

    function stepPrev() {{
        killAnimate();
        frameNum--;
        if (frameNum < 0) frameNum = maxFrameNum;
        showFrame();
    }}

    function speedUp() {{
        delay = Math.max(10, delay - 20); // Decrease delay (faster)
        updateSpeedDisplay();
    }}

    function slowDown() {{
        delay = delay + 20; // Increase delay (slower)
        updateSpeedDisplay();
    }}
    
    function updateSpeedDisplay() {{
        var speedDisplay = document.getElementById('speedDisplay');
        if (speedDisplay) {{
            speedDisplay.innerHTML = delay + 'ms';
        }}
    }}

    function reloadPage() {{
        window.location.reload();
    }}

    function addLogEntry() {{
        var table = document.getElementById('logTable').getElementsByTagName('tbody')[0];
        // Check if entry already exists
        var rows = table.rows;
        for (var i = 0; i < rows.length; i++) {{
             if (rows[i].cells[0].innerHTML === imageNames[frameNum]) {{
                 alert('Entry for this image already exists!');
                 return;
             }}
        }}

        var newRow = table.insertRow();
        var cell1 = newRow.insertCell(0);
        var cell2 = newRow.insertCell(1);
        var cell3 = newRow.insertCell(2);
        var cell4 = newRow.insertCell(3);
        var cell5 = newRow.insertCell(4);

        cell1.innerHTML = imageNames[frameNum];
        cell2.innerHTML = '<select onchange="saveData()"><option value="">Select...</option><option value="Flare">Flare</option><option value="Filament eruption">Filament eruption</option></select>';
        cell3.innerHTML = '<select onchange="saveData()"><option value="">Select...</option><option value="Yes">Yes</option><option value="No">No</option></select>';
        cell4.innerHTML = '<input type="text" placeholder="Enter notes..." style="width:100%" oninput="saveData()">';
        cell5.innerHTML = '<button onclick="deleteRow(this)">Delete</button>';
        
        saveData();
    }}

    function deleteRow(btn) {{
        var row = btn.parentNode.parentNode;
        row.parentNode.removeChild(row);
        saveData();
    }}

    function saveData() {{
        var table = document.getElementById('logTable');
        var rows = table.rows;
        var data = [];
        // Skip header (row 0)
        for (var i = 1; i < rows.length; i++) {{
            var filename = rows[i].cells[0].innerText;
            var eventType = rows[i].cells[1].getElementsByTagName('select')[0].value;
            var highSpeed = rows[i].cells[2].getElementsByTagName('select')[0].value;
            var notesInput = rows[i].cells[3].getElementsByTagName('input')[0];
            var notes = notesInput ? notesInput.value : "";
            data.push({{filename: filename, eventType: eventType, highSpeed: highSpeed, notes: notes}});
        }}
        try {{
            localStorage.setItem('eventLog_' + window.location.pathname, JSON.stringify(data));
        }} catch (e) {{
            console.warn("LocalStorage not available:", e);
        }}
    }}

    function loadData() {{
        try {{
            var stored = localStorage.getItem('eventLog_' + window.location.pathname);
            if (stored) {{
                var data = JSON.parse(stored);
                var table = document.getElementById('logTable').getElementsByTagName('tbody')[0];
                table.innerHTML = "";
                
                for (var i = 0; i < data.length; i++) {{
                    var newRow = table.insertRow();
                    var cell1 = newRow.insertCell(0);
                    var cell2 = newRow.insertCell(1);
                    var cell3 = newRow.insertCell(2);
                    var cell4 = newRow.insertCell(3);
                    var cell5 = newRow.insertCell(4);

                    cell1.innerHTML = data[i].filename;

                    var eventType = data[i].eventType || "";
                    var highSpeed = data[i].highSpeed || "";

                    var eventSelect = '<select onchange="saveData()"><option value="">Select...</option>';
                    eventSelect += '<option value="Flare"' + (eventType === 'Flare' ? ' selected' : '') + '>Flare</option>';
                    eventSelect += '<option value="Filament eruption"' + (eventType === 'Filament eruption' ? ' selected' : '') + '>Filament eruption</option></select>';
                    cell2.innerHTML = eventSelect;

                    var speedSelect = '<select onchange="saveData()"><option value="">Select...</option>';
                    speedSelect += '<option value="Yes"' + (highSpeed === 'Yes' ? ' selected' : '') + '>Yes</option>';
                    speedSelect += '<option value="No"' + (highSpeed === 'No' ? ' selected' : '') + '>No</option></select>';
                    cell3.innerHTML = speedSelect;
                    
                    cell4.innerHTML = '<input type="text" placeholder="Enter notes..." style="width:100%" value="' + (data[i].notes ? data[i].notes.replace(/"/g, '&quot;') : "") + '" oninput="saveData()">';
                    cell5.innerHTML = '<button onclick="deleteRow(this)">Delete</button>';
                }}
            }}
        }} catch (e) {{
            console.warn("Cannot load from LocalStorage:", e);
        }}
    }}
    
    function cleanLog() {{
        if (confirm("Are you sure you want to delete all entries from the log? This cannot be undone.")) {{
            var tableBody = document.getElementById('logTable').getElementsByTagName('tbody')[0];
            tableBody.innerHTML = "";
            localStorage.removeItem('eventLog_' + window.location.pathname);
        }}
    }}

    function downloadCSV() {{
        var table = document.getElementById('logTable');
        var rows = table.rows;
        var csvContent = "data:text/csv;charset=utf-8,Filename,Event Type,High Speed,Notes\\n";

        for (var i = 1; i < rows.length; i++) {{ // Skip header
            var filename = rows[i].cells[0].innerText;
            var eventType = rows[i].cells[1].getElementsByTagName('select')[0].value;
            var highSpeed = rows[i].cells[2].getElementsByTagName('select')[0].value;
            var notesInput = rows[i].cells[3].getElementsByTagName('input')[0];
            var notes = notesInput ? notesInput.value : "";
            csvContent += filename + "," + eventType + "," + highSpeed + "," + notes.replace(/,/g, " ") + "\\n";
        }}
        
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "image_log.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }}

    // Preload images
    function preloadImages() {{
        for (var i = 0; i < {num_frames}; i++) {{
            aniFrames[i] = new Image();
            aniFrames[i].src = imageFiles[i];
        }}
    }}
    """
    
    # HTML structure
    html_content = f"""
    <html>
    <head>
        <title>Image Sequence Viewer</title>
        <script>{js_script}</script>
        <style>
            body {{ text-align: center; font-family: sans-serif; }}
            .controls {{ margin: 10px 0; }}
            button {{ padding: 8px 15px; font-size: 16px; margin-right: 5px; cursor: pointer; }}
            #frameCounter {{ font-weight: bold; margin-bottom: 5px; }}
            #logSection {{ margin: 20px auto; width: 80%; text-align: left; }}
            #logContainer {{ max-height: 300px; overflow-y: auto; border: 1px solid #ddd; margin-top: 10px; }}
            #logTable {{ width: 100%; border-collapse: collapse; }}
            #logTable th, #logTable td {{ border: 1px solid #ddd; padding: 8px; }}
            #logTable th {{ background-color: #f2f2f2; position: sticky; top: 0; z-index: 10; }}
            #logControls {{ margin-top: 20px; text-align: center; }}
        </style>
    </head>
    <body onload="preloadImages(); startAnimate(); loadData();">
        <h2>Image Sequence ({num_frames} frames, <span id="speedDisplay">{delay_ms}ms</span>)</h2>
        <div id="frameCounter">1/{num_frames}</div>
        <img name="imageWindow" src="{files_js[0]}" alt="Image sequence animation">
        
        <div class="controls">
            <button onclick="startAnimate()">Play</button>
            <button onclick="killAnimate()">Stop</button>
            <button onclick="stepPrev()">Previous</button>
            <button onclick="stepNext()">Next</button>
            <button onclick="speedUp()">Faster</button>
            <button onclick="slowDown()">Slower</button>
            <button onclick="reloadPage()">Reload</button>
        </div>

        <div id="logSection">
            <h3>Event Log</h3>
            <div id="logControls">
                 <button onclick="addLogEntry()">Add Current Image to Log</button>
                 <button onclick="cleanLog()">Clean Log Chart</button>
                 <button onclick="downloadCSV()">Download Log as CSV</button>
            </div>
            
            <div id="logContainer">
            <table id="logTable">
                <thead>
                    <tr>
                        <th style="width: 20%">Filename</th>
                        <th style="width: 15%">Event Type</th>
                        <th style="width: 10%">High Speed</th>
                        <th style="width: 45%">Notes</th>
                        <th style="width: 10%">Action</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            </div>
        </div>
    </body>
    </html>
    """

    # Write the HTML file
    with open(output_html, 'w') as f:
        f.write(html_content)

    # Open in web browser
    print(f"Opening {output_html} in web browser...")
    #webbrowser.open(f'file://{os.path.realpath(output_html)}')

# --- Example Usage ---
# Replace 'your_image_directory' with the path to your image folder
#image_folder_path = '/Users/denis/Analysis/20170423/sddi_spectral_velR0B_mov/' 
image_folder_path = 'maps_temp/' 
create_image_sequence_html(image_folder_path)
