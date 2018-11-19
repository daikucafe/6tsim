curl -s \
  --form-string "token=aixbth1uq993jemq2juuhjur5d5q6e" \
  --form-string "user=MgzqvlvXrk9JrGhch1L8BjQfuKxJC7" \
  --form-string "message=Empezamos!" \
  https://api.pushover.net/1/messages.json

python runSim.py --config config_per_of0.json

curl -s \
  --form-string "token=aixbth1uq993jemq2juuhjur5d5q6e" \
  --form-string "user=MgzqvlvXrk9JrGhch1L8BjQfuKxJC7" \
  --form-string "message=config_per_of0.json listo" \
  https://api.pushover.net/1/messages.json

python runSim.py --config config_per_taof.json

curl -s \
  --form-string "token=aixbth1uq993jemq2juuhjur5d5q6e" \
  --form-string "user=MgzqvlvXrk9JrGhch1L8BjQfuKxJC7" \
  --form-string "message=config_per_taof.json listo" \
  https://api.pushover.net/1/messages.json

python runSim.py --config config_var_of0.json

curl -s \
  --form-string "token=aixbth1uq993jemq2juuhjur5d5q6e" \
  --form-string "user=MgzqvlvXrk9JrGhch1L8BjQfuKxJC7" \
  --form-string "message=config_var_of0.json listo" \
  https://api.pushover.net/1/messages.json

python runSim.py --config config_var_taof.json

curl -s \
  --form-string "token=aixbth1uq993jemq2juuhjur5d5q6e" \
  --form-string "user=MgzqvlvXrk9JrGhch1L8BjQfuKxJC7" \
  --form-string "message=config_var_taof.json listo" \
  https://api.pushover.net/1/messages.json