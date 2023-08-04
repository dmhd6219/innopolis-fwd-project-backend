# Hiroshi Matsumoto Site Remake Backend

![License](https://img.shields.io/github/license/dmhd6219/innopolis-fwd-project-backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-red.svg)](https://fastapi.tiangolo.com/)

Backend for [Innopolis FWD Project](https://github.com/dmhd6219/innopolis-fwd-project). Was
Was created as Final Project for FWD (FrontEnd Web Development) course at Innopolis University.

This repository contains the backend code for the remake of Hiroshi Matsumoto's personal website. The backend is powered
by FastAPI, a modern, fast, web framework for building APIs with Python.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

The backend of the Hiroshi Matsumoto Site Remake serves as the API server responsible for handling data requests from
the frontend. It works seamlessly with the Svelte frontend to provide a smooth user experience.

## Features

- Fast and efficient API powered by FastAPI.
- JSON-based data communication with the frontend.
- Integration with the frontend to serve content dynamically.

## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/dmhd6219/innopolis-fwd-project-backend.git
cd innopolis-fwd-project-backend
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the project dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

To run the backend server and access the API, use the following command:

```bash
uvicorn inno-fwd.main:app --reload
```

The server will start running at `http://localhost:8000`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
