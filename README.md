# cvostriker

## CVMS Curriculum Vitae Management System

The Curriculum Vitae Management System (CVMS) is a web-based application designed to manage and showcase your CV. This system features both a public interface and an administrative interface, allowing users to easily manage their CVs online. The project is built using Flask and leverages multiple servers instance to handle different parts of the application.

### Featuries

-- **Public Interface**: A user-friendly public page where visitors can view your CV.
-- **Administrative Interface**: A secure admin page where you can update anad manage your CV details.
- **Multi-Server Architecture**: The application is structured to run different components on separate servers for better organization and scalability.

### Project Structure

flask-Project/ | ├── admin/ │ └── app.py  ├── public/ │ └── app.py │ └── main.py

### How to Run

1. **Run Servers**:
```
$ cd flask-Project
python run_servers.py
```

2. Access the application:
- Public Interface: http://localhost:5001
- Admin Interface: http://localhost:5002
- Main Interface: http://localhost:5000

### Requeriments

* Python 3
* Flask
* SQLAlchemy

### Instalation

1. Clone the repository:
```
git clone https://github.com/yourusername/your-repo-name.git
```

2. Install dependencies:
```
pip install -r requirements.txt
```

# Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

# License

This project is licensed under the MIT License.