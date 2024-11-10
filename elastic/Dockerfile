FROM elasticsearch:8.6.2

ENV ES_JAVA_OPTS="-Xms200m -Xmx200m"
ENV discovery.type="single-node"
ENV path.repo="/usr/share/elasticsearch/snapshots"
ENV xpack.security.enabled="false"

COPY elastic/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]