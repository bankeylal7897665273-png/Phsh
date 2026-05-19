from http.server import BaseHTTPRequestHandler
import json
import base64
from io import BytesIO
from PIL import Image
from rembg import remove

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        req_body = json.loads(post_data)
        
        base64_image = req_body.get('image')
        clones = int(req_body.get('clones', 1))
        
        # Decode Image
        image_data = base64.b64decode(base64_image.split(",")[1])
        input_image = Image.open(BytesIO(image_data))
        
        # Remove Background
        output_image = remove(input_image)
        output_image = output_image.convert("RGBA")
        
        # Create A4 Size Canvas (Ujal Kakas) - 2480x3508 pixels for 300dpi
        a4_canvas = Image.new('RGB', (2480, 3508), (255, 255, 255))
        
        # Resize passport photo (e.g., 2x2 inches -> 600x600 px)
        output_image.thumbnail((600, 600))
        
        # Paste Clones on Canvas dur dur pr
        x_offset, y_offset = 100, 100
        for i in range(clones):
            a4_canvas.paste(output_image, (x_offset, y_offset), output_image)
            x_offset += 700
            if x_offset > 2000:
                x_offset = 100
                y_offset += 700
                
        # Convert back to base64 to send to frontend
        buffered = BytesIO()
        a4_canvas.save(buffered, format="JPEG")
        final_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "success",
            "result_image": f"data:image/jpeg;base64,{final_img_str}"
        }).encode())
