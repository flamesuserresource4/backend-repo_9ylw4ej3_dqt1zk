"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
- ContactMessage -> "contactmessage" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Hashed password with salt")


class BlogPost(BaseModel):
    """
    Blog posts collection schema
    Collection name: "blogpost"
    """
    title: str = Field(..., description="Post title")
    slug: str = Field(..., description="URL slug")
    excerpt: str = Field(..., description="Short summary")
    content: str = Field(..., description="Markdown or HTML content")
    author: str = Field(..., description="Author name")
    cover_image: Optional[str] = Field(None, description="Optional cover image URL")
    published: bool = Field(True, description="Whether post is published")


class ContactMessage(BaseModel):
    """
    Contact messages collection schema
    Collection name: "contactmessage"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message body")
