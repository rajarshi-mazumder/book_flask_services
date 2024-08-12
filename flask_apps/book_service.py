from flask import Flask, request, jsonify, Blueprint
from config import Config
from models.books import db, Book, Author, BookCategory, BookDetails, Category
from models.collections import Collection
from .auth_service import auth_required
import hashlib
import json
from .storage_service import generate_pre_signed_url

books_service = Blueprint("services", __name__)

# app = Flask(__name__)


first_request_handled = False

def book_data_map(book):

    cover_img_pre_signed_url= generate_pre_signed_url(book.cover_img_path)
    book_data = {
            'id': book.id,
            'book_id': book.book_id,
            'title': book.title,
            'description': book.description,
            'cover_img_path': book.cover_img_path,
            'author': {'name': book.author.name} if book.author else None,
            'categories': [{'category_id': category.id, 'category_name': category.name} for category in book.categories],
            'details_hash': book.details_hash,
            'cover_img_pre_signed_url':cover_img_pre_signed_url,
        }
    return book_data

@books_service.before_request
def create_tables():
    global first_request_handled
    if not first_request_handled:
        db.create_all()
        first_request_handled = True

@books_service.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category_name = data['name']
    
    try:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
            return jsonify({'message': 'Category created successfully'}), 201
        else:
            return jsonify({'message': 'Category already exists'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_service.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book_id = data['book_id']
    title = data['title']
    description = data['description']
    cover_img_path = data.get('cover_img_path')
    author_name = data['author']['name'] if data.get('author') else None
    categories_data = data.get('categories', [])

    try:
        author = None
        if author_name:
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.commit()

        categories = []
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(name=cat_data['name'])
                db.session.add(category)
                db.session.commit()
            categories.append(category)

        new_book = Book(
            book_id=book_id,
            title=title,
            description=description,
            cover_img_path=cover_img_path,
            author=author
        )
        new_book.categories = categories

        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_service.route('/books', methods=['GET'])
@auth_required
def get_books(current_user):
    books_list = []

    # page= request.args.get("page", 1, type=int)
    # per_page= request.args.get("per_page", 2, type=int)
    # pagination  = Book.query.paginate(page=page, per_page=per_page, error_out= False)

    # for book in pagination.items:
    #     book_data = book_data_map(book)
    #     books_list.append(book_data)

    # return jsonify({"books": books_list, "total_page": pagination.pages, "current_page": pagination.page, "has_next":pagination.has_next})

    books = Book.query.all()
    print(f"made RDS call to get books")
    try:
        for book in books:
            book_data = book_data_map(book)
            books_list.append(book_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

    return {"books": books_list}

@books_service.route("/categories", methods=['GET'])
def get_categories():
    categories= Category.query.all()

    categories_map=[]

    for c in categories:
        categories_map.append({
            "category_id": c.id,
            "category_name":c.name
            })

    return jsonify({
        "categories": categories_map
    })

@books_service.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    book_data = book_data_map(book)
    return jsonify(book_data)

@books_service.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    book = Book.query.get_or_404(id)

    book.book_id = data['book_id']
    book.title = data['title']
    book.description = data['description']
    book.cover_img_path = data.get('cover_img_path')

    author_name = data['author']['name'] if data.get('author') else None
    categories_data = data.get('categories', [])

    try:
        if author_name:
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.commit()
            book.author = author
        else:
            book.author = None

        categories = []
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(name=cat_data['name'])
                db.session.add(category)
                db.session.commit()
            categories.append(category)
        book.categories = categories

        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_service.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_service.route('/author', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    author_list = []
    for author in authors:
        author_data = {
            'id': author.id,
            'name': author.name,
        
        }
        author_list.append(author_data)
    return jsonify(author_list)

@books_service.route('/books/<int:id>/details', methods=['POST'])
def add_book_details(id):
    data = request.get_json()
    book = Book.query.get_or_404(id)

    book_chapters = data.get('book_chapters', [])

    try:
        # Check if BookDetails already exists for the book
        book_details = BookDetails.query.filter_by(book_id=book.id).first()
        
        if not book_details:
            # Create new BookDetails
            book_details = BookDetails(
                book_id=book.id,
                book_chapters=book_chapters
            )
            db.session.add(book_details)
            db.session.commit()
            book.book_details_id = book_details.id
        else:
            # Update existing BookDetails
            book_details.book_chapters = book_chapters
            
        # Calculate hash
        book_details_hash = hashlib.sha256(json.dumps(book_chapters).encode()).hexdigest()
        book.details_hash = book_details_hash

        db.session.commit()
        return jsonify({'message': 'Book details added/updated successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@books_service.route("/books/<int:id>/details", methods=["GET"])
def get_book_details(id):
    # Query the book with the given id
    book = Book.query.get_or_404(id)
    
    # Get book details if available
    book_details = BookDetails.query.filter_by(book_id=book.id).first()
    
    # Prepare the response
    book_data = {
        'id': book.id,
        'book_details': {
            'book_chapters': book_details.book_chapters if book_details else None
        } if book_details else None
    }
    
    return jsonify({"book_data": book_data})


@books_service.route("/collections", methods=["POST"])
def add_collection():
    try:
        data = request.get_json()
        id = data.get('id')
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        collection_img_path= data.get('collection_img_path')
        categories_data = data.get('categories', [])

        if id:
            existing_collection= Collection.query.get(id)
            if existing_collection:
                return jsonify({"error": "Collection with this ID already exists"}), 400
      
        if not name:
            return jsonify({"error": "Collection name is required"}), 400
        
        categories = []
        for cat_name in categories_data:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.session.add(category)
                db.session.commit()
            categories.append(category)

    
        collection= Collection(
            name=name,
            collection_img_path= collection_img_path,
            description= description,
            categories=categories
        )
        db.session.add(collection)
        db.session.commit()

        return jsonify({"message": "Collection added successfully", "collection": collection.name}), 200
    except Exception as e:
        return jsonify({f"message":"Error creating collection {e}"}), 500

@books_service.route("/collections")
def get_collections():
    try:
        collections= Collection.query.all()
        collections_list=[]
        for collection in collections:
            collection_data={
                "id":collection.id,
                "name": collection.name,
                "description": collection.description,
                "collection_img_path":collection.collection_img_path,
                "categories":[{'category_id': category.id, 'category_name': category.name} for category in collection.categories],
            }
            collections_list.append(collection_data)
        
        return jsonify({"collection_data": collections_list}), 200
    except:
        return jsonify({"message":"Error fetching collections"}), 500
