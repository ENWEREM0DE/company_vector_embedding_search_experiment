# Company Vector Search

A Streamlit-based web application that performs semantic vector search on company descriptions using OpenAI embeddings and MongoDB vector search capabilities.

## Features

- **Password Protection**: Secure access with authentication (password: email ebube198@gmail.com to request password)
- **Semantic Search**: Use natural language to find similar companies based on their descriptions
- **Vector Embeddings**: Powered by OpenAI's text-embedding-ada-002 model
- **MongoDB Vector Search**: Leverages MongoDB's vector search index for fast similarity matching
- **Filtering**: Filter results by industry and other criteria
- **USA Focus**: All searches are automatically filtered for US-based companies
- **Interactive UI**: Clean and responsive Streamlit interface
- **Session Management**: Stay logged in during your session with logout functionality

## Prerequisites

- Python 3.8+
- MongoDB Atlas account with vector search index configured
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd test
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URI=your_mongodb_connection_string_here
   ```

## Configuration

### MongoDB Setup

1. Ensure you have a MongoDB Atlas cluster with a database named `marovi_db_prod`
2. Your collection should be named `companies_new_data_load`
3. Create a vector search index named `vector_index_for_company_search` on the `company_description_embedding` field

### Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for generating embeddings
- `MONGO_URI`: MongoDB connection string (typically starts with `mongodb+srv://`)

## Usage

1. **Start the application**
   ```bash
   streamlit run companyDescriptionEmbeddingsSearch.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8501`

3. **Authenticate**
   - Enter the password: `ExecScience`
   - Click "Login" to access the application

4. **Search for companies**
   - Enter a company description in the text area
   - Optionally filter by industries (comma-separated)
   - Adjust search parameters as needed
   - Click "Search for Similar Companies"

5. **Logout (optional)**
   - Use the "Logout" button in the top-right corner to return to the login screen

## Project Structure

```
test/
├── companyDescriptionEmbeddingsSearch.py  # Main Streamlit application
├── requirements.txt                       # Python dependencies
├── .env                                  # Environment variables (create this)
├── .gitignore                           # Git ignore patterns
├── README.md                            # Project documentation
└── venv/                               # Virtual environment (auto-generated)
```

## Features Explained

### Vector Search Parameters

- **Max results**: Number of results to fetch from the database (1-10,000)
- **Candidates**: Number of candidates to search through (affects search quality vs. speed)

### Filtering Options

- **Industries**: Filter results by specific industries (comma-separated list)
- **Country**: Automatically filtered to USA-based companies only

## Technical Details

- **Embedding Model**: OpenAI's text-embedding-ada-002
- **Database**: MongoDB with vector search capabilities
- **Web Framework**: Streamlit for the user interface
- **Caching**: Built-in caching for embeddings and database connections to improve performance

## Error Handling

The application includes comprehensive error handling for:
- OpenAI API connection issues
- MongoDB connection failures
- Invalid search parameters
- Missing environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Security Notes

- Never commit your `.env` file or API keys to version control
- Use environment variables for all sensitive configuration
- Consider using Streamlit's secrets management for production deployments

## Troubleshooting

### Common Issues

1. **OpenAI API Error**: Check your API key and account credits
2. **MongoDB Connection Error**: Verify your connection string and network access
3. **No Search Results**: Try broader search terms or check your vector index configuration
4. **Performance Issues**: Adjust the number of candidates or results to optimize for your use case

## License

[Add your license here] 