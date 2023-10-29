import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd

cpu_df = pd.read_csv("C:/Users/owens/Downloads/Laptop Comparison - Passmark CPU stats.csv")
gpu_df = pd.read_csv("C:/Users/owens/Downloads/Laptop Comparison - Passmark GPU stats.csv")

# Convert DataFrames to lists and filter out non-string values
cpu_list = [x for x in cpu_df["CPU"].tolist() if isinstance(x, str)]
gpu_list = [x for x in gpu_df["Price1"].tolist() if isinstance(x, str)]

def get_best_match(text, choices):
    best_match = None
    best_score = 0
    for choice in choices:
        score = fuzz.token_sort_ratio(text, choice)
        if score > best_score:
            best_score = score
            best_match = choice
    return best_match, best_score


def parse_specs(text, cpu_list, gpu_list):
    specs = {}
    
    # Extract name
    name = re.match(r"^(.*?):", text)
    if name:
        specs["Name"] = name.group(1)
    
    # Find closest CPU match
    cpu_match = get_best_match(text, cpu_list)
    print("CPU match:", cpu_match)  # Debug line
    if cpu_match and cpu_match[1] > 60:  # You can adjust the threshold
        specs["CPU"] = cpu_match[0]
    
    # Find closest GPU match
    gpu_match = get_best_match(text, gpu_list)
    print("GPU match:", gpu_match)  # Debug line
    if gpu_match and gpu_match[1] > 60:  # You can adjust the threshold
        specs["GPU"] = gpu_match[0]
    
    # Extract RAM and storage
    gb_matches = re.findall(r"(\d+GB)", text)
    tb_matches = re.findall(r"(\d+TB)", text)
    if gb_matches:
        gb_values = sorted([int(re.search(r"\d+", match).group()) for match in gb_matches])
        if len(gb_values) == 1 or gb_values[0] < 128:
            specs["RAM"] = str(gb_values[0]) + "GB"
        if len(gb_values) > 1:
            specs["Storage"] = str(gb_values[1]) + "GB"
    if tb_matches:
        specs["Storage"] = tb_matches[0]
    
    return specs

# Example usage
#cpu_list = ["Intel Core i5-11400H", "Intel Core i7-12700H"]
#gpu_list = ["GeForce GTX 1650 (Mobile)", "RTX 3060"]
text = "ACER Nitro 5 Gaming Notebook 15.6\" FHD Intel Core i5-11400H GTX 1650 8GB 256GB SSD Windows 11 Home, NH.QEKAA.007"
print(parse_specs(text, cpu_list, gpu_list))