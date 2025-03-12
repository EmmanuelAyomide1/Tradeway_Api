# Tradeway API Style Guide

This document outlines the coding standards and contribution guidelines for the Tradeway API. All contributors are expected to adhere to these rules to maintain consistency, readability, and quality across the codebase.

## Table of Contents
- [Steps to run](#steps-to-run)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Views](#views)
- [Documentation](#documentation)
- [Branching Strategy](#branching-strategy)
- [Pull Requests](#pull-requests)
- [Non-Compliance](#non-compliance)

## Steps to run
- Clone the repository
    ```
    git clone https://github.com/EmmanuelAyomide1/Tradeway_Api.git
    ```
- Enter project directory
    ```
    cd Tradeway_Api
    ```
- Install project requirements
    ```
    cd requirements
    pip install -r base.txt
    ```
- Run project
    ```
    python manage.py runserver
    ```
Swagger documentation is available at http://localhost:8000

## Project Structure
This project uses Django REST Framework to build RESTful APIs. All API-related code should follow the conventions outlined below.

## Coding Standards
- **Python Style**: Follow PEP 8 guidelines unless explicitly overridden by this style guide.
- **Autopep8**: Utilize autopep8 to format code before making a PR
  - bash:
    ```
    autopep8 --in-place --aggressive --aggressive --recursive <directory>
    ```

## Views
- **Class-Based Views Only**: All views must be implemented using Class-Based Views (CBVs). Function-Based Views (FBVs) are not permitted.
- **ViewSets for Related Operations**: Use ViewSets when implementing related views for the same resource (list, retrieve, update, etc.). This reduces code duplication and provides a more consistent API interface.
  - Example:
    ```python
    # Preferred for related CRUD operations
    from rest_framework import viewsets
    
    class UserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        
        def get_serializer_class(self):
            if self.action == 'list':
                return UserListSerializer
            return UserDetailSerializer
    ```
- **Generic Views Preference**: For standalone endpoints, utilize DRF's Generic Views. Minimize the use of `APIView` unless absolutely necessary for complex custom logic.
  - Example:
    ```python
    # Preferred for standalone endpoints
    from rest_framework import generics
    
    class UserListView(generics.ListAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        
    # Use only when necessary
    from rest_framework.views import APIView
    
    class CustomView(APIView):
        ...
    ```

## Documentation
- **Swagger Documentation**: All endpoints must be documented using Swagger (via drf-yasg or similar). Ensure every endpoint includes:
  - Summary
  - Description
  - Possible response codes
  - Request/response examples
  - Example
    ```python
    class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
      """
      Retrieve, update or delete an order.
      
      GET: Returns the details of a specific order
      PUT: Updates the order details
      DELETE: Removes the order
      """
      queryset = Order.objects.all()
      serializer_class = OrderSerializer
    ```

## Branching Strategy
- Feature Branches: All new features must be developed in a new branch with the naming convention feature/<feature-name> (e.g., feature/add-user-authentication).
- No Direct Pushes to Main: Direct pushes to the main branch are prohibited. All changes must go through a Pull Request (PR).

## Pull Requests
- Each feature must be submitted through a pull request
- PRs must be reviewed and approved by team leaders before merging
- PRs that do not follow the style guide will be rejected
- Provide a clear description of the changes in your PR

## Non-Compliance
- PRs that do not follow these guidelines will not be merged.
- Team leaders are responsible for enforcing these standards during code reviews.
