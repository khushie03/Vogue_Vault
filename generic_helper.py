import re

def get_str_from_product_dict(product_dict):
    result = ", ".join([f"{value} {key}" for key, value in product_dict.items()])
    return result



def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""

if __name__ == "__main__" :
    extract_session_id("")