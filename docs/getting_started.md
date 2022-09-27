# Getting Started

- [Getting Started](#getting-started)
  - [What's the point of this?](#whats-the-point-of-this)
  - [Why SheetShuttle?](#why-sheetshuttle)
  - [Before we jump in](#before-we-jump-in)
    - [Code Dependencies](#code-dependencies)
    - [Setting up API keys](#setting-up-api-keys)
    - [How does SheetShuttle work?](#how-does-sheetshuttle-work)
  - [Let's start coding](#lets-start-coding)
    - [Why is this code so messy?](#why-is-this-code-so-messy)
    - [Time to write some tests](#time-to-write-some-tests)
  - [How do I run this thing?](#how-do-i-run-this-thing)
  - [Ok, but now what?](#ok-but-now-what)
    - [SheetShuttle needs some fixes](#sheetshuttle-needs-some-fixes)
    - [Write your own plugins](#write-your-own-plugins)

## What's the point of this?

This guide should help you get started as a developer of SheetShuttle. Specifically, it will help you understand
the purpose of the project, clarify some of the reasoning behind the design decisions, and much more.
It's inevitable that some details will be missed here, so **this should be a living document**.
Always feel free to update it as the implementation changes and when you have new ideas/questions/requests about the project.

## Why SheetShuttle?

The purpose of SheetShuttle is to create infrastructure to automate:

1. Retrieving data from Google Sheets
2. Processing this data through user-defined plugins
3. Publishing the processed data through different ways on GitHub

You might say: "This is very broad, I don't think much was explained here", but that's exactly the point.
SheetShuttle is simply the infrastructure that allows more specific problems to be solved. We want to allow the
user to define their own approach to solving a problem, and use our infrastructure do implement it.
With that in mind, SheetShuttle is meant to be plugin-friendly. This means that the user can write their
own code and integrate it into SheetShuttle workflow.

## Before we jump in

I know you're really excited to jump in and start coding but we gotta set up few things first.
This is not the most fun part, but the good thing is that you'll only have to do it once!

### Code Dependencies

SheetShuttle uses many dependencies that you're likely already familiar with. Tools like Python and poetry
are used in many labs and practicals in the CS department and you likely already have some experience with them.
If you don't already have these two installed, then you should start by doing that. I recommend installing Python
through Pyenv or another equivalent since it makes switching to the right version easier. As for Poetry, you can
find the instructions in the [official website](https://python-poetry.org/docs/). It's also worth taking some time
to review poetry commands and how they're used.
Once you have both, Python and Poetry installed, make sure to run `poetry install` inside your repository home. This will
install all needed dependencies on your Python virtualenv.

### Setting up API keys

Setting up API keys is very important to be able to use SheetShuttle. If you're interested in using the GoogleSheets side,
then you must set up a service account and have your authentication token and other information stored on your computer.
[This guide](./Google_API_Setup.md) shows the needed steps to set up a service account.

As for the GitHub side of things, you will need a personal access token store on your computer to be able to use
the GitHub features of SheetShuttle. This [online guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
has the steps needed to do that.

**Make sure to keep all keys and tokens secure. DO NOT commit files containing keys, it will cause a security problem and invalidate your keys.**

**Side note**: If you're planning to create Google Sheets service account or get a GitHub access token, I recommend that you use a throwaway account.
Do not use your personal Google or GitHub account to avoid any issues that could happen such as loss of personal data or other problems we can't anticipate.

### How does SheetShuttle work?

There are three main components in SheetShuttle: Google Sheets handler, GitHub handler, and the user defined plugin. There are some requirements
for the user defined plugin but it could include anything the user wants. As for the two handlers, they provide the API that the user defined
plugin can use.

Both handlers operate on the same concepts and they share the following:

- Require configuration file that is either user written or automatically generated
- Configuration file must follow the schema outlined in the infrastructure of each handler
  - **NOTE:** The schema guide is a _very_ important resource. You can find it [here](./schemas.md)
- Each handler iterates through the configuration and makes a series of API requests to send out/retrieve the
    data specified in the configuration files

## Let's start coding

Now that you know the concept behind SheetShuttle, you can start contributing to the project!
Make sure you follow the code of conduct and the contribution guide while you write code and
send it for review.

### Why is this code so messy?

A lot of the code in SheetShuttle was written as proof of concept to see that we can implement something
that links Google Sheets and GitHub. This means that there is plenty of room to polish it up, refactor, and make
it more clear to read and understand. If you find some parts to be confusing, missing documentation, or outright
disorganized, feel free to go in and make the necessary changes! Many linters are also included in the project
to make sure that you're following industry standards of code hygiene and keeping things clean and tidy.

### Time to write some tests

Testing is very important when you're adding new changes or making fixes to existing problems. We don't want
to ship a broken product so we always want to make sure that SheetShuttle is working as expected. The existing
test suite covers most of the code in the tool but there is room for improvement. Any changes to the infrastructure
code should be accompanies with some testing to validate that things are running correctly.

## How do I run this thing?

After you run `poetry install`, the command you need is `poetry run sheetshuttle <your_arguments>`. If you want to know more about the available arguments,
you can run `poetry run sheetshuttle -h` to display the help message.

## Ok, but now what?

### SheetShuttle needs some fixes

There are some existing open issues in the repository that need to be addressed. Some of them are major problems, and others are smaller ones.
This is one of the main priorities to make sure that the infrastructure is bug-free before we start using it.

### Write your own plugins

Once existing issues have been resolved, we can start adding new features in the form of plugins! These plugins
can look very different depending on what you want them to do. However, they should probably live somewhere else and
not with the infrastructure code. So please don't commit plugins directly to this repository since we're only planning
to ship the infrastructure and everything else is an addon.
