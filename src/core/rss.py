# rss module

def get_entry_link(entry):
	for fallback in ["link", "link_url", "default"]:
		if fallback in entry:
			return entry[fallback]
	return None

def ensure_entry_has_id(entry):
	if not "id" in  entry:
		link = get_entry_link(entry)
		if link:
			entry["id"] = link
