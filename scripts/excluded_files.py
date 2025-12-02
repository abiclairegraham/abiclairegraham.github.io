import csv

input_csv = "/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths.csv"       # your original CSV file
filtered_csv = "/content/drive/MyDrive/Personal Projects/media_catalogue_instagram_with_paths_filtered.csv"    # new CSV file with rows removed
deleted_csv = "/content/drive/MyDrive/Personal Projects/deleted_rows.csv"

excluded=[ #powerlifting
          "18016370719899807.webp",
         "18022156784076253.webp",
         "18159959638235425.webp",
         "17928952432505003.jpg",
         "17928952432505003.jpg",
         "17854092700617633.jpg",
         "17945150098113514.jpg",
         "18007660543172043.jpg",
         "18018043879133852.jpg",
         "17981237539198996.jpg",
         "18007660543172043.mp4",
         "17905113820394921.jpg",
         "17916921145347127.jpg",
         "17908277254366587.jpg",
         "18030195313246345.jpg",
         "18003021040226141.jpg",
         "17862419155613903.jpg",
         "17875702018457172.jpg",
         "17984249167151069.jpg",
         "18070575166090999.jpg",
         "17963212666002901.jpg",
         "17867158066258061.jpg",
         "17933904988179143.jpg",
         "17874724030275440.jpg",
         "17963002954095050.jpg",
         "17937577615207599.jpg",
         "17984249167151069.mp4",
         "17930760109190454.jpg",
         "17868152494254648.jpg",
         "17931236812130402.jpg",
         "17888294107240418.jpg",
         "17958295486085794.jpg",
          #origami
          "17987096227045789.jpg" 
          #makeup
            ]

target_column = "filename_raw"   # name of the CSV column containing image paths

# Counters
total_rows = 0
kept_rows = 0
deleted_rows = 0

with open(input_csv, newline="", encoding="utf-8") as infile, \
     open(filtered_csv, "w", newline="", encoding="utf-8") as filtered_out, \
     open(deleted_csv, "w", newline="", encoding="utf-8") as deleted_out:

    reader = csv.DictReader(infile)

    # Prepare writers
    filtered_writer = csv.DictWriter(filtered_out, fieldnames=reader.fieldnames)
    deleted_writer = csv.DictWriter(deleted_out, fieldnames=reader.fieldnames)

    # Write headers to both output files
    filtered_writer.writeheader()
    deleted_writer.writeheader()

    # Process rows
    for row in reader:
        total_rows += 1
        image_path = row[target_column]

        # If row should be deleted (match found)
        if any(excluded_name in image_path for excluded_name in excluded):
            deleted_writer.writerow(row)
            deleted_rows += 1
        else:
            filtered_writer.writerow(row)
            kept_rows += 1

# Print summary
print("Total input rows:", total_rows)
print("Kept rows (filtered.csv):", kept_rows)
print("Deleted rows (deleted_rows.csv):", deleted_rows)
