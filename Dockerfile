FROM python

# CONTAINER CONSTRUCTION
######################

# create new user to avoid root privileges
RUN useradd -ms /bin/bash sanjego
USER sanjego
WORKDIR /home/sanjego

# copy source code
# --chown is not available in my current docker version
COPY main.py .
COPY sanjego sanjego
COPY rulesets rulesets
COPY searching searching

# set up dependencies
RUN pip install --user --upgrade pip && \
    pip install --user sacred

# create volume directory explicitly to avoid root owner
RUN mkdir results
VOLUME results

# RUN CONFIGURATION
######################

# set default run parameter values
ENV HEIGHT=1 \
    WIDTH=1 \
    RULES=base \
    MAX_PLAYER_STARTS=True

# call the main program
# whose arguments can be altered using environment variables
CMD ["sh", "-c", "python main.py with \
     height=$HEIGHT \
     width=$WIDTH \
     rules=$RULES \
     max_player_starts=$MAX_PLAYER_STARTS"]
