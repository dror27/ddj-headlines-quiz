curl -s $1 | xmllint 2>/dev/null --html --xpath '//div[@id="fsb"]/p/a[3]/@href' - | cut -d '"' -f 2
