




    pattern = re.compile(r"([\S]+(\s[\S]+)*)\s+([\S]+(\s[\S]+)*)\s+(\d+)\s+(\d+)\s+([\w\/\.\-]+)")#+\s?[a-zA-Z0-9]+$") \s+(\d+)\s+([\w/\-]+)
    #res = re.match(pattern, test_string)

    # for i in range(pattern.groups+1):
    #     print(res.group(i))
    bad_parses = 0
    for i, line in enumerate(data):
        # if i == 20:
        #     break
        if i < 11:
            continue
        parsed = re.match(pattern, line)
        if parsed == None:
            bad_parses += 1
            print("Failed to parse line")
            print(line)
            continue
        
        form_type = parsed.group(1)
        company_name = parsed.group(3) # groups 2 and 4 are meaningless
        cik = parsed.group(5) # group(3) is meaningless
        date = parsed.group(6)
        rel_url = parsed.group(7)
        #if form_type == "D" or form_type == "D/A":
        #print("Company Name: {1}\n\tForm Type: {0}\n\tCIK: {2}\n\tURL: {3}\n".format(form_type, company_name, cik, rel_url))
        #if i == 10:
        # if line.startswith("Form Type"):
        #     guide = line
        #     comp_name_idx = guide.find("Company Name")
        #     cik_idx = guide.find("CIK")
        #     date_idx = guide.find("Date Filed")
        #     url_idx = guide.find("File Name")
        # if i == 12:
        #     print(line[:comp_name_idx])
        #     print(line[comp_name_idx:cik_idx])
        #     print(line[cik_idx:date_idx])
        #     print(line[date_idx:url_idx])
        #     print(line[url_idx:])
        #    return 0
        #if line.startswith("D ") or line.startswith("D/A "):
        #    print(line)
    print(bad_parses)
