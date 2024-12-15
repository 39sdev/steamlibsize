import re

#appid = input("Enter appid of dirty vdf: ")

def extract_vdf(data):
    # Use a regular expression to find the start of VDF-like content
    match = re.search(r'(".*?"\s*{)', data, re.DOTALL)
    if match:
        # Start extraction from the matched point
        start = data.find(match.group(1))
        end = data.rfind('}')
        if end != -1:

            return data[start:end + 1]
    else:
        pass
        #raise ValueError("No valid VDF data found in input")
# def vdf_clean(appid):
#     # Clean file's content
#     with open(f"{appid}_dirty.vdf","r") as inputfile:
#         dirty_content = inputfile.read()
#         vdf_data = extract_vdf(dirty_content)

#     with open(f"{appid}.vdf", "w") as output:
#         output.write(vdf_data)