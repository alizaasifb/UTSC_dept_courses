from bs4 import BeautifulSoup
from pyvis.network import Network
from InquirerPy import inquirer
import requests
import re


def get_course_name(course):
  course_name = course.find("h3")
  if course_name is not None:
    return course_name.text.split(" -")[0][:-2].strip()
  else:
    return None

def get_course_prereqs(course):
  course_prereq = course.find("span", class_="views-field views-field-field-prerequisite")
  if course_prereq is not None:
      prereq_list = re.findall(r'\b\w*H3\b', course_prereq.text[14:])
      prereq_list = [prereq[:-2] for prereq in prereq_list]
      return prereq_list
  else:
    return None

def get_all_courses(department):
  department_page = requests.get("https://utsc.calendar.utoronto.ca/section/" + department)
  soup = BeautifulSoup(department_page.content, "lxml")
  department_courses_section = soup.find("div", class_="view-courses-view")
  courses = department_courses_section.find_all("div", class_="views-row")
  return courses

def get_course_color(course_name): 
  color = ""
  if (course_name[3] == 'A'):
    color = "red"
  elif (course_name[3] == 'B'):
    color="orange"
  elif (course_name[3] == "C"):
    color="yellow"
  else:
    color="green"
  return color

def create_graph(department, graph):
  courses = get_all_courses(department)
  if courses is not None:
    for course in courses:
      if course is not None:
        course_name = get_course_name(course)
        if course_name is not None:
          color= get_course_color(course_name)
          graph.add_node(course_name, color=color, shape="circle", size=25, title=course.text, font={'size': 30})
          course_prereqs = get_course_prereqs(course)
          if course_prereqs is not None:    
            for course_prereq in course_prereqs:
              color = get_course_color(course_prereq)
              graph.add_node(course_prereq, color=color, shape="circle", size=25, title=course_prereq, font={'size': 30})
              graph.add_edge(course_prereq, course_name, color="grey")

def draw_graph(department):
    graph = Network(directed=True, font_color='black', height='700', width='100%')
    create_graph(department, graph)
    graph.show('graph.html', notebook=False) 
    with open('graph.html', 'r') as file:
        html_content = file.read()
    new_html_content = html_content.replace('<body>', f'<body><h1 style="text-align:center;">{department} Courses</h1>', 1)
    with open('graph.html', 'w') as file:
        file.write(new_html_content)
    
def get_department_choice():
  choices = ["Computer-Science", "Biological-Sciences", "Mathematics", "Statistics", "Chemistry", "Anthropology", "Philosophy"]
  choice = inquirer.select( message="Please choose one of the following options:", choices=choices).execute()
  return choice

selected_department = get_department_choice()
draw_graph(selected_department)
