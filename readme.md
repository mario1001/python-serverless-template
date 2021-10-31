# Python Serverless backend service template

It's intended to be a framework based-template for serverless projects.

The recommended version to use is Python 3.8, main reason is that AWS lambda functions are strictly limited by that one.

This template is intended to be oriented for serverless microservices with some of the design patterns inherited from Spring framework in Java development. There's DI along with an application context (not that rough and heavy of course).

There's certain concepts you need to know before exploring this template:

* Template terminology:
  * Core: Main components of the template (connections, context and decorators).
  * Component: Object/instance with base class ContextABC in project (abstract class for defining our components), based on Spring component/bean concept to work with. Every controller, service and repository
  abstract classes are *components* in the template.
  * Resources: Main resources defined for the project (this could be config vars or some memory-instances defined, could be constants or shared features also).
  * Entity: Domain model object (domain package). There are different types of domain objects: Models (database entities definition) enum table configuration along with relationships and database requests options for repository usages.
  * Bean: Component to inject by the core framework.
<br />

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#running-tests">Running tests</a>
    </li>
    <li>
      <a href="#structure-and-modules">Structure and modules</a>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#local-development">Local development</a></li>
        <li><a href="#core">Core explanation</a></li>
      </ul>
    </li>
    <li><a href="#authors">Authors</a></li>
  </ol>
</details>
<br />

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development or testing purposes.
<br/>

### Prerequisites

You will need to install Python 3+ firstly, recommended version is 3.8 as noted before. Working with Python could be by several ways:

* Installing SO system version from official page using installers: [Python 3.8 installers](https://www.python.org/downloads/release/python-380/) and using this one for projects.
* Using virtual environment with [venv](https://docs.python.org/es/3.8/library/venv.html), but you will still need Python installed on your system.
<br />

Also it's recommended to install [git](https://git-scm.com/downloads) along with the development process.

### Installing

Download this repository or clone it with the following command:

```sh
git clone https://github.com/mario1001/python-serverless-template.git
```

For running the project you will need to install the dependencies. Run the following command for modules clean installation:

```sh
cd python-serverless-template
python -m pip install -r requirements.txt
```

This will install the project modules as python packages along with the rest of the shared modules (folder is called site-packages for the interested ones).

But you also require AWS Chalice (the base framework for building our projects) by just running this command:

```sh
python -m pip install chalice
```

You should read the official documentation about [AWS Chalice](https://aws.github.io/chalice/main.html) before exploring and understanding the template modules. Chalice provides a local way to tests the lambda functions without using Docker or AWS SAM utilities.

When installing the chalice package, it would give you also the chalice command line functionality (you can test it in console with: *chalice* "option" or just *chalice*). 
<br/>
<br/>

## Running tests

This project contains different type of tests: unit tests and integration tests. Please make sure that you
use a in-memory database for integration testing or the default option with temporary database provided by
pifpaf module before executing the tests with pytest command.

To install Pytest use this:

```sh
$ python -m pip install pytest
$ python -m pip install pytest-cov
```

So then you just can access to the project main directory location (*python-serverless-template* in our case) and run the following:

```sh
$ python -m pytest
```
<br />

## Structure and modules

```
  python-serverless-template/                # Project main directory
  ├── README.md                              # Project explanation file
  ├── chalicelib/                            # AWS Chalice library with custom modules
  │     ├── __init__.py                         # Chalice library main module
  │     ├── controllers/                        # Controller layer
  │     │   └── __init__.py                       # Controller main module (controller component)
  │     ├── core                                # Core components (internal project functionalities)
  │     │   └── (...)                             # (...)
  │     ├── domain                              # Domain layer
  │     │   ├── models                             # Project models
  │     │   ├── request_options.py                 # Request options for database queries
  │     │   └── sql_config.py                      # SQL config enumeration module (constants for tables)
  │     ├── services                            # Service layer
  │     │   ├── __init__.py                       # Service main module (service component)
  │     │   ├── cache_service.py                  # Cache service module (cache service class)
  │     │   └── main_service.py                   # Main service module (main service definition)
  │     ├── repositories                        # Repository layer
  │     │   ├── __init__.py                       # Repository main module (repository component)
  │     │   ├── mysql_repository.py               # MySQL repository module (base repository definition)
  │     │   └── mysql_statement.py                # MySQL statement module
  │     ├── dto                                 # DTO layer
  │     │   ├── requests                          # DTO requests module
  │     │   ├── responses                         # DTO responses module
  │     │   └── cache                             # DTO cache module
  │     ├── config.ini                          # Project Configuration file
  │     └── resources.py                        # Project main resources module
  ├── .gitignore                          # Git ignore file (files not for uploading in the repo)
  ├── tests                               # Tests (unit, integration, enpdoint, etc...)
  │    └── (...)
  ├── app.py                              # Main application importing the project modules
  ├── .pylintrc                           # Pylint initial hook for avoiding sonarqube errors for custom modules
  ├── requirements.txt                    # Requirements file for python dependencies
  └── build.gradle                        # Gradle configuration for Bamboo
```

So here goes the explanation about the template architecture, designed to be a mini-framework template for different type of projects (microservices or some other features/components). It's intended to be an event-oriented architecture with the following layers:
* **Handler layer**: Also called routers, seems like a soft-controller layer displayed by distinct resources/business logic (one module per business model). It will request the specific methods in controller layer with the help of the core dependency injector technique.
* **Controller layer**: Main controller layer based in Spring framework controllers/RESTcontrollers. Displays a security role (or checks in terms of authorization/authentication) with the specific security controllers (if needed). The project Primaria Digital does not require much security but all of these features would be as components of this layer.
It's the main layer in the application because: flow control, HTTP requests managed by applying the business logic (with the help of service layer) and forming the responses in case of needs (also featuring common responsabilities).
* **Service layer**: Manages controller requests with a main service with a dispatcher for the tasks, each task could be requested by different services (each resource service to be named). There's some services defined in the template: Cache service and the service abstract base class. Deals always with DTO requests/responses but never creating/managing database entity operations (do not confuse service layer with repository layer).
* **Repository layer**: Main layer for dealing with domain model items, these instances would be in domain package (defined in the models package), service layer would request these services for getting domain objects and forming the specific responses as DTO for controllers. There's a *BaseRepository* class defined in the *mysql_repository* module for many features provided for projects (since session providers, custom commit operations prepared, entity searched with table name or custom native SQL queries with MySQL statements executions).
* **Logging layer**: Form a system logger base class with several features (mainly ones) for logs with parameters or with different formats. Also could be provided a different logger handler with distinct instances for logging (with files also for no serverless purposes)
* **Exception layer**: Manages the distinct exceptions in the application: One module
per layer for dealing with different exceptions (also importing here the AWS Resources library RESTful API exceptions).
* **Core layer**: Special layer with core modules: Database Client pool, definition of application context and decorators for components in our application. Defines the framework-utilities to use (like DI dependency injector features or logs programmed). 
<br/>
<br/>

## Usage

### Local development

With all installations done, one can simply run the template locally with:

```sh
chalice local
```

This would rise up a server in the port 8000 in localhost (or by default 127.0.0.1 as address IP).
There are two API Gateway endpoints services here:
* Users handler: 
  * /users GET
  * /users/{id} GET (being id an integer ID)
  * /users POST
  * /users PUT

There's other feature commands (for creating base projects or deployment for example) but won't be used in this project for now. Deployment would be without the command line tool (that task corresponds to infrastructure).

### Core explanation

This section is reserved for the core functionality, we have several decorators here that can be used:
- **register**: For registering a class in the application context for injection, you just need to provide one or more parameters (can be numbers or strings) and core would register the bean with specific key. Key is formed with arguments passed to the decorator.
- **inject**: Main method for activating the DI (Dependency Injection) for shared instances in the project. This one contains two parameters:
  - *ref*: Specify the class reference (class type in the end), reference used for building instances internally.
  - *values*: Iterable with a bunch of parameters (whatever you put here would be used in constructor forming).
  With iterable, we mean a dictionary, list or tuple with arguments provided.
- **logger**: Main tag for making logs with the function decorated and the arguments provided.
- **classproperty**: Decorator for creating a class property (like *@property* for instances but for classes) in a class.

*DI (Dependency injection) Notes*

¿How to register classes? Just put a *register* decorator in the constructor (__init__ method of the class). Also for core to detect it, you will need to extend/inherit from a special core class (called ContextABC). Injection decorators would provide instances registered by keys any time you would use the inject command (register goes straight for the inject).

At last but not at least, another important thing to mention here is that core injection is provided on two sides: A class property called **instance** will be created on the reference provided (ref parameter in inject decorator) and also will put the bean in an attribute (could perfectly be a property declared) named as the reference passed in the place using the decorator (class or module which injects the bean).

E.g. Having a class with name *ColorService*, injecting a bean of reference *ColorRepository* in a property called color_repository (snake case always to be pythonic).

<br/>

## Testing

There's two types of tests in this template (it's a bit important to distinct them) and exposed in packages:

* Integration tests: More like a full endpoint-service supported tests. It's related with the
application functionality with its layers interaction.
* Unit tests: Base unit test with no component interaction (no layer interaction), they are basically
a standalone way for testing the functionality composing the system application.

<br/>

We use [Pytest](https://docs.pytest.org/en/6.2.x/) for making the integration/unit tests, some of the configuration is associated within ini file along with the conftest fixtures file. Common mocks are usually setup in this conftest module (shared resources in the end).

What is a fixture in Pytest? A simple component loaded in time execution for our tests, it's more like
setting different pieces of code in certain test functions. Also fixtures provides the real mocks or patchs (depending of the use) for certain situations with different services.

When programming tests you should ALWAYS be very carefully about the DI in this template, causing the more errors/problems out there in most situations, top-level imports are especially loaded before the fixture mocks (setting the properly configuration in pytest should make the job here). There are certain tips that can be followed along the test development, would explain with examples:

```python
import app
from pytest import fixture
from chalice.test import Client

@fixture
def mock_client():
  with Client(app.app) as client:
    yield client
```

As I mentioned before, you have two options: prepare the mocks before importing project fixtures or just issuing a little trick with config files for pytest. Having that fixture (provided with AWS Chalice client pytest fixture) would not work well with our test examples, the right way would be this:

```python
from pytest import fixture
from chalice.test import Client

@fixture
def mock_client():
  import app

  with Client(app.app) as client:
    yield client
```

Maybe it's probably the ridiculous thing you have seen in programming, but template projects would work
this way when having dependency injections in our original code. ORDER real matters for tests.

The same goes for the following syntax:

```python
from module import function

function()
```

Best practices do not recommend these imports when having multiple module dependencies in giant projects, should be a better implementation this way for the patchs to work well (reserve monkeypatchs also for fixtures the best you can):

```python
import module

module.function()
```

<br/>

## Authors

* **Mario Benito** - *Initial work*