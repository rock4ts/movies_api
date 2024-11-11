FROM elasticsearch:8.6.2

ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
ENV discovery.type="single-node"
ENV path.repo="/usr/share/elasticsearch/snapshots"
ENV xpack.security.enabled="false"

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]