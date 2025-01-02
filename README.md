# PersonaPicks

PersonaPicks is a personalized movie and book tracker designed around the MBTI personality framework. This Django-based project provides recommendations for movies and books based on your MBTI type, allows you to add them to watch/read lists, and lets you create personalized lists. You can also explore profiles of other users based on their MBTI types and follow them.

## Features

- **Personalized Recommendations**: Get book and movie suggestions tailored to your MBTI type.
- **Watchlist and Readlist Management**: Add and manage movies and books you wish to watch or read.
- **Custom Lists**: Create and manage personalized lists for books and movies.
- **Social Features**: Browse other user profiles by MBTI type, follow them, and check compatibility scores.
- **Activity Tracking**: Keep track of your activity, including list updates and connections.
- **Feedback System**: Share feedback on recommendations and improve the system.

## Project Setup

Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/laibak24/PersonaPicks
   cd personapicks
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   Install the required packages from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**:
   Apply the migrations to set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Development Server**:
   Start the Django development server:
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000/` to start using PersonaPicks.

## Usage

1. **Register and Log In**: Create an account or log in to access personalized features.
2. **Explore Recommendations**: Browse book and movie recommendations tailored to your MBTI type.
3. **Manage Lists**: Add movies to your watchlist or books to your readlist. Create custom lists for easy organization.
4. **Socialize**: Explore profiles of other users, follow them, and view compatibility scores.
5. **Give Feedback**: Share feedback to help refine recommendations.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- Thanks to the contributors and the Django community for their support.
- Special thanks to users providing valuable feedback for improvements.

