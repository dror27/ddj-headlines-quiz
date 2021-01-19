FEEDS_URL=$1
FEEDS_DOMAIN=$2
FEEDS_LANG=$3
FEEDS_NUM=$4

paste -d ','  <(./g_name.sh $FEEDS_URL) <(./g_feed.sh $FEEDS_URL) <(./g_site.sh $FEEDS_URL) | \
	head -$FEEDS_NUM | \
	awk -F, -v FEEDS_DOMAIN=$FEEDS_DOMAIN -v FEEDS_LANG=$FEEDS_LANG '\
		END {
			print("\n]\n");
		}
		{
			if ( NR == 1 )
				printf("[\n");
			else
				printf(",\n");
			printf(" {\n");
			printf("  \"domain\": \"%s\",\n", FEEDS_DOMAIN);
			printf("  \"land\": \"%s\",\n", FEEDS_LANG);
			printf("  \"name\": \"%s\",\n", $1);
			printf("  \"rss\": \"%s\",\n", $2);
			printf("  \"url\": \"%s\",\n", $3);
			printf("  \"userAgent\": \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36\"\n");

			printf(" }");
		}
	'
