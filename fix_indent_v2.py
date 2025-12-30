
path = 'app/api/endpoints/forecast.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Locate the start of the block
    if "p_title = str(p.get('title', '')).upper()" in line:
        # Keep this line
        new_lines.append(line)
        # Add the fixed block immediately
        # indent based on current line?
        indent = line[:line.find("p_title")]
        
        # Add the rest of the logic with proper indentation
        new_lines.append(f'{indent}if "780 LITROS" in p_title and "INTEX" in p_title:\n')
        new_lines.append(f'{indent}    # Search in sales_map\n')
        new_lines.append(f'{indent}    for r_item_id, r_qty, r_sku in realized_sales_query:\n')
        new_lines.append(f'{indent}        r_sku_str = str(r_sku or "").upper()\n')
        new_lines.append(f'{indent}        if "780" in r_sku_str and ("SUNSET" in r_sku_str or "BOMBA" in r_sku_str):\n')
        new_lines.append(f'{indent}            real_qty += float(r_qty or 0)\n')
        
        # Skip the original bad lines until we hit the exception block
        skip = True
        continue
    
    if skip:
        if "except Exception as e:" in line:
            skip = False
            new_lines.append(line) # Add the except line back
        continue
        
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Rewrote panic block.")
