import os 

sub_dirs = os.listdir("Africa/")

for country_code in sub_dirs:
    all_files = os.listdir(os.path.join("Africa", country_code))

    for f in all_files:

        cur_path = os.path.join("Africa", country_code, f)
        new_path = os.path.join("Africa", country_code, f.replace("blocks", "buildings"))

        print(cur_path + "  -->  " + new_path)
        os.rename(cur_path, new_path)
        

