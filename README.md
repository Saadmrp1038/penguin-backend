# PenguinLLM Backend

## Overview

The PenguinLLM backend powers a knowledge base platform with both admin and client-facing features. Admins can submit questions, answers, and website links, which are automatically integrated into the knowledge base. The client side allows users to interact with a chatbot that pulls answers from the knowledge base. If a user finds an answer unsatisfactory, they can report it, prompting admins to update the knowledge base.

To enrich the knowledge base, the system is pre-populated with data from platforms like Fiverr and Upwork, providing a comprehensive set of articles and information.

> **Note**: The web scraping functionality that scrapes pages of submitted websites is managed through a separate repository. For more details, refer to the [Penguin Scraping Backend](https://github.com/Saadmrp1038/penguin-scraping-backend).

## Features

### Admin Panel:
- Admins can submit and manage questions, answers, and website links.
- The system integrates submitted websites into the knowledge base by connecting to the scraping backend, which extracts relevant content from those websites.

### Client Chat Interface:
- Users interact with a chatbot that retrieves answers from the knowledge base.
- Users can report unsatisfactory chatbot responses, which flags them for admin review and potential updates.

### Automated Scraping:
- A separate repository, [Penguin Scraping Backend](https://github.com/Saadmrp1038/penguin-scraping-backend), handles the scraping of submitted websites.
- Platforms like Fiverr and Upwork have been scraped to pre-populate the knowledge base with a large set of articles.

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/): A high-performance web framework for building APIs with Python.
- **Database**: [PostgreSQL](https://www.postgresql.org/): Used for storing the knowledge base data and user reports.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/): Handles database interactions.
- **Web Scraping**: [Scrapy](https://scrapy.org/): Deployed via a separate repository for scraping websites and platforms like Fiverr and Upwork.

### Deployment
- **Automation**: GitHub Actions handles Continuous Deployment. Pushing code to the GitHub repository triggers an automated deployment process to a DigitalOcean droplet.
- **Server**: The application is hosted on a DigitalOcean droplet, with [Nginx](https://www.nginx.com/) used for reverse proxy and load balancing.

## API Documentation

The PenguinLLM backend provides comprehensive and interactive API documentation built with FastAPI’s Swagger UI. You can explore all the available endpoints and their usage in detail.

- **Live API Documentation**: [https://penguapi.priyolab.net/docs](https://penguapi.priyolab.net/docs)

## Installation and Setup

### Prerequisites
- **Python 3.9+**: Ensure that Python is installed on your system.
- **PostgreSQL**: Set up a PostgreSQL database to manage the knowledge base.
- **GitHub Actions**: Properly configure CI/CD workflows using GitHub Actions for automated deployment.
- **Nginx**: Configure Nginx on the DigitalOcean droplet for serving the application.

### Deployment

Deployment is automated using GitHub Actions. Pushing code to the main branch triggers a workflow that builds and deploys the backend to a DigitalOcean droplet.

To configure the workflow:
1. Update the `.github/workflows/deploy.yml` file with your deployment details.
2. Push changes to the repository. The GitHub Actions workflow will automatically deploy the changes to your droplet.

## Related Repositories

- **Penguin Scraping Backend**: [https://github.com/Saadmrp1038/penguin-scraping-backend](https://github.com/Saadmrp1038/penguin-scraping-backend)
  - This repository handles the scraping of websites submitted by admins, and integrates the scraped data into the PenguinLLM knowledge base.
