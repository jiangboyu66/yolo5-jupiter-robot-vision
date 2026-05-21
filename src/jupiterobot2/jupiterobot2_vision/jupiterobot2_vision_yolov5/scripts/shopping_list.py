# #!/usr/bin/env python3
import cv2
import numpy as np

# UI parameters
width, height = 500, 400
bg_color = (255, 255, 255)  # white background
line_color = (0, 0, 0)      # black lines
text_color = (0, 0, 0)
row_height = 50
num_rows = 6
col_widths = [200, 150, 100]  # Item, Quantity, Price

# Column headers
columns = ["Item", "Quantity", "Price"]

# Initialize shopping data with empty rows
shopping_data = [["", "", ""] for _ in range(num_rows)]

def draw_table(data):
    # Create blank image
    ui_img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Draw column headers
    x = 0
    for i, col in enumerate(columns):
        cv2.rectangle(ui_img, (x, 0), (x + col_widths[i], row_height), line_color, 2)
        cv2.putText(ui_img, col, (x + 10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        x += col_widths[i]

    # Draw rows
    for r, row in enumerate(data):
        y1 = (r + 1) * row_height
        y2 = y1 + row_height
        x = 0
        for c, value in enumerate(row):
            cv2.rectangle(ui_img, (x, y1), (x + col_widths[c], y2), line_color, 2)
            cv2.putText(ui_img, str(value), (x + 10, y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
            x += col_widths[c]

    # Draw total row at the bottom
    total_y1 = (num_rows + 1) * row_height
    total_y2 = total_y1 + row_height
    cv2.rectangle(ui_img, (0, total_y1), (sum(col_widths), total_y2), line_color, 2)
    cv2.putText(ui_img, f"Total: ${calculate_total(data):.2f}", (10, total_y1 + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Shopping List", ui_img)
    cv2.waitKey(1)

def calculate_total(data):
    total = 0.0
    for row in data:
        try:
            price_str = row[2].replace("$", "")
            total += float(price_str) if price_str else 0
        except:
            continue
    return total

if __name__ == "__main__":
    import time

    # Show empty table first
    draw_table(shopping_data)
    time.sleep(2)

    # Example: fill some items
    # shopping_data[0] = ["Ajinomoto", 2, "$11.00"]
    # shopping_data[1] = ["NTMilo", 1, "$3.20"]
    # shopping_data[2] = ["Nestle Milo", 3, "$10.50"]

    while True:
        draw_table(shopping_data)
        if cv2.waitKey(100) & 0xFF == 27:  # ESC to exit
            break

    cv2.destroyAllWindows()
