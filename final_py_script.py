import re
import json

def convert_curl(input_curl):
    # Extract the URL
    url_match = re.search(r"'(https://[^\s]+)'", input_curl)
    url = url_match.group(1) if url_match else None
    
    # Extract the method (default to GET if no method or data is found)
    method_match = re.search(r"--request (\w+)", input_curl)
    if method_match:
        method = method_match.group(1)
    else:
        method = 'POST' if re.search(r"--data(?:-raw)?", input_curl) else 'GET'
    
    # Extract the headers
    headers = re.findall(r"--header '(.*?)'", input_curl)
    
    # Extract the JSON body (use --data or --data-raw) and make it a single line
    body = re.search(r"--data(?:-raw)? '(.*?)'", input_curl, re.DOTALL)
    json_body = body.group(1).replace('\n', '').strip() if body else None

    # If json_body is not None, clean and try to parse it
    if json_body:
        # Replace double double quotes with single double quotes
        json_body = json_body.replace('""', '"')
        try:
            # Parse and re-dump to ensure correct escaping
            json_data = json.loads(json_body)
            json_body = json.dumps(json_data)  # This ensures proper escaping
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {json_body} - {str(e)}")
            json_body = None

    # Build the new curl command
    new_curl = f"curl -i -s -k -X $'{method}' "

    # Add headers
    for header in headers:
        new_curl += f"-H $'{header}' "
    
    # Add body if present
    if json_body:
        new_curl += f"--data $'{json_body}' "
    
    # Add the URL
    if url:
        new_curl += f"$'{url}'"
    
    return new_curl

def process_curl_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Read the content of the input file
        content = infile.read()
        
        # Split the content into separate curl commands using '####' as a separator
        curl_commands = content.split('####')
        
        # Process each curl command
        for curl_command in curl_commands:
            # Remove any leading/trailing whitespace
            curl_command = curl_command.strip()
            
            if curl_command:
                # Convert the curl command
                converted_curl = convert_curl(curl_command)
                
                # Write the converted curl to the output file
                outfile.write(converted_curl + "\n")
                
                # Add the separator after each converted curl
                outfile.write('####\n')

# Specify input and output file paths
input_file = 'curls.txt'   # Path to your input file
output_file = 'output_curls.txt'  # Path to your output file

# Process the file
process_curl_file(input_file, output_file)
