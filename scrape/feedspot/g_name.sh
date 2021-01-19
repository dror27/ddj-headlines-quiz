curl -s $1 | xmllint --html --xpath '//div[@id="fsb"]/h3/a/text()' - 2>/dev/null | cut -d '|' -f 1 | awk '{$1=$1;print}' | sed 's/ RSS Feed$//g'
