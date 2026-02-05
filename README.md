# Bridge Exporter

### Phase 2: The "War Room" Dashboard (Grafana)
![war-room](https://github.com/user-attachments/assets/ce354272-1e72-42d7-8a3b-f45c9748c3ec)

### Phase 3: The "Architecture" Challenge (Critical Thinking)

Based on my knowledge, I would implement Kafka in this case. 
The data will be sent from Node E (Vietnam) to the corresponding topic in Kafka. Now, when the data is saved in the Kafka topic, it will stay safely there and wait to be consumed by the consumer in Finland when it goes online. 

When I set up Kafka, I will also increase the Kafka replication factors to 3 or 4. By that, when 1 broker dies, the others will replace it and avoid losing data.

Saving the consumer offset to keep track, so when the consumer reconnects, it will resume from the last offset saved. Also, define the auto_offset_reset="earliest" to ensure consumers capture all data from the beginning. 
