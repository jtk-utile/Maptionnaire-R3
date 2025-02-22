# Use Miniconda as the base image (official Conda image)
FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR /app

# Copy the environment.yml file to the container
COPY shiny_mini.yml /app/shiny_mini.yml

# Install the Conda environment
RUN conda env create -f shiny_mini.yml && \
    conda clean --all --yes

# Set the environment path
ENV PATH="/opt/conda/envs/shiny_mini/bin:$PATH"

# Activate Conda environment (needed for CMD execution)
SHELL ["/bin/bash", "-c"]

# Copy your PyShiny app files into the container
COPY . /app

# Expose the port PyShiny runs on (adjust if necessary)
EXPOSE 8000

# Default command to run the PyShiny app
CMD ["shiny", "run", "app.py", "--port", "8000", "--host", "0.0.0.0"]
