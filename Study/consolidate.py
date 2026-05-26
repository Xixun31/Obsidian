import os
import re
import urllib.parse

study_dir = os.path.dirname(os.path.abspath(__file__))
daily_dir = os.path.join(study_dir, "Daily")

folders = {
    "Subjects": os.path.join(study_dir, "Subjects"),
    "others": os.path.join(study_dir, "others"),
    "mine": os.path.join(study_dir, "mine")
}

# Matches [[Topic]] or [[Topic|Label]]
wikilink_pattern = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

def parse_frontmatter_manual(content):
    if not content.startswith("---"):
        return [], [], "2026-03-30", "other"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return [], [], "2026-03-30", "other"
    fm_text = parts[1]
    
    tags = []
    aliases = []
    date_val = "2026-03-30"
    type_val = "other"
    
    current_key = None
    for line in fm_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if key == 'date':
                date_val = val
                current_key = None
            elif key == 'type':
                type_val = val
                current_key = None
            elif key == 'tags':
                current_key = 'tags'
                if val:
                    if val.startswith('[') and val.endswith(']'):
                        tags = [t.strip() for t in val[1:-1].split(',')]
                        current_key = None
                    else:
                        tags.append(val)
            elif key == 'aliases':
                current_key = 'aliases'
                if val:
                    if val.startswith('[') and val.endswith(']'):
                        aliases = [a.strip() for a in val[1:-1].split(',')]
                        current_key = None
                    else:
                        aliases.append(val)
            else:
                current_key = None
        elif line.startswith('-'):
            val = line[1:].strip()
            if current_key == 'tags':
                tags.append(val)
            elif current_key == 'aliases':
                aliases.append(val)
    return tags, aliases, date_val, type_val

def consolidate():
    # 1. Map all existing topic files and their aliases to their paths
    topic_files = {} # maps topic_name -> (path, folder_key)
    keywords_map = {} # maps keyword/alias -> topic_name
    
    for fkey, fpath in folders.items():
        if not os.path.exists(fpath):
            continue
        for f in os.listdir(fpath):
            if not f.endswith(".md"):
                continue
            topic_name = f[:-3]
            filepath = os.path.join(fpath, f)
            
            topic_files[topic_name] = (filepath, fkey)
            keywords_map[topic_name] = topic_name
            
            with open(filepath, 'r', encoding='utf-8') as file_obj:
                content = file_obj.read()
                
            # Parse H1 title
            h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
                keywords_map[title] = topic_name
                eng_parts = re.findall(r"\(([^)]+)\)", title)
                for ep in eng_parts:
                    keywords_map[ep.strip()] = topic_name
                    
            # Parse aliases
            _, aliases, _, _ = parse_frontmatter_manual(content)
            for alias in aliases:
                keywords_map[alias.strip()] = topic_name

    # 2. Gather daily logs
    if not os.path.exists(daily_dir):
        print("Daily notes directory not found!")
        return
        
    # maps topic_name -> list of (date, text)
    logs_by_topic = {topic: [] for topic in topic_files.keys()}
    
    daily_files = sorted([f for f in os.listdir(daily_dir) if f.endswith(".md")])
    for df in daily_files:
        # date is the filename (e.g., 2026-05-26)
        date_val = df[:-3]
        filepath = os.path.join(daily_dir, df)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
                
        # Split body into sections by horizontal rules
        sections = re.split(r'\n\s*(?:-{3,}|\*{3,}|(?:-\s+){2,}-)\s*(?:\n|$)', body)
        
        for section in sections:
            section_stripped = section.strip()
            if not section_stripped:
                continue
                
            # Check what wikilinks are mentioned in this section
            links = wikilink_pattern.findall(section_stripped)
            matched_topics = set()
            for link in links:
                decoded_link = urllib.parse.unquote(link.strip())
                # Match against keywords map
                if decoded_link in keywords_map:
                    matched_topics.add(keywords_map[decoded_link])
                    
            # Check for plain text keywords as fallback if no wikilinks matched
            if not matched_topics:
                # Sort keywords by length descending
                sorted_kws = sorted(keywords_map.keys(), key=len, reverse=True)
                for kw in sorted_kws:
                    if kw in section_stripped:
                        matched_topics.add(keywords_map[kw])
                        break # Only match the longest keyword in this segment
                        
            for topic in matched_topics:
                if (date_val, section_stripped) not in logs_by_topic[topic]:
                    logs_by_topic[topic].append((date_val, section_stripped))

    # 3. Update each topic file with the sorted logs
    for topic, (filepath, fkey) in topic_files.items():
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        frontmatter = ""
        body = raw_content
        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                body = parts[2]
                
        # Strip existing logs section
        body_cleaned = body
        log_header_match = re.search(r"\n\n##\s+(?:相關記錄|歷程日誌)\s*\(?(?:Records|Course Logs)?\)?", body)
        if log_header_match:
            body_cleaned = body[:log_header_match.start()]
            
        # Determine logs section header name based on folder
        if fkey == "Subjects":
            header_name = "歷程日誌 (Course Logs)"
        else:
            header_name = "相關記錄 (Records)"
            
        logs_content = f"\n\n## {header_name}\n\n"
        topic_logs = logs_by_topic.get(topic, [])
        topic_logs.sort(key=lambda x: x[0]) # sort by date
        
        if topic_logs:
            for l_date, l_text in topic_logs:
                logs_content += f"### [[{l_date}]]\n{l_text}\n\n"
        else:
            logs_content += "尚無記錄。\n"
            
        # Reconstruct and write back
        fm_block = f"---{frontmatter}---\n\n" if frontmatter else ""
        new_content = fm_block + body_cleaned.strip() + logs_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Consolidated: {fkey}/{topic}.md with {len(topic_logs)} logs")

if __name__ == "__main__":
    consolidate()
