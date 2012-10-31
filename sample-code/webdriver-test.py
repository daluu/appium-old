#! /usr/bin/python
from selenium import webdriver
from random import randint

# generate two random numbers
num1 = randint(1,9)
num2 = randint(1,9)

# create a webdriver instance
command_url = 'http://localhost:4723/wd/hub'
iphone = webdriver.DesiredCapabilities.IPHONE
print '\nconnecting to web driver @ ' + command_url
driver = webdriver.Remote(command_url, iphone)

# enter the two numbers into the fields
fields = driver.find_elements_by_tag_name('textField')
print 'Entering "' + str(num1) + '" into the first text field' 
fields[0].send_keys(num1)
print 'Entering "' + str(num2) + '" into the second text field'
fields[1].send_keys(num2)

# submit the form
buttons = driver.find_elements_by_tag_name('button')
print 'Submitting the form'
buttons[0].click()

# validate the sum
# add validation here
print '\033[92m' + 'SUM = ' + str(num1+num2) + '\033[0m'

# quit the webdriver instance
print 'Quitting webdriver\n'
driver.quit()
