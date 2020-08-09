Feature: Timer
   The timer window

Background: Prepared Window
    Given the window
    And the user selects "testing" category
    And the "Fall" semester

Scenario: Working
    Given the running timer
    When the user works
    Then the duration is greater than 0
    And the timer is running
    And the start button is disabled

Scenario: Pause
    Given the running timer
    When the user clicks pause
    Then the timer is stopped
    And the duration is greater than 0
    And the start button is enabled

Scenario: Reset
    Given the running timer
    When the user clicks reset
    Then the duration is 0
    And the timer is stopped
    And the start button is enabled

Scenario: Submit
    Given the running timer
    When the user clicks submit
    Then the app submits the duration of any seconds
    And the duration is 0
    And the start button is enabled


Scenario: Manual Input
    Given the manual tab
    And the user enters
        "1" for hours
        "2" for minutes
        "3" for seconds
    When the user clicks submit
    Then the app submits the duration of 3723 seconds
    And the fields are reset
