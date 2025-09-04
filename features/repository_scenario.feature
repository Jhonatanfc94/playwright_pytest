Feature: My GitHub page
  Test example for learning BDD
  
  Scenario Outline: Verify Order success message shown in details page
    Given the user is on the <page_name> page
    And the user click on the tab repositories
    When the user search <project>
    Then link to the <project> is shown in results
    Examples:
      | project           | page_name                        | 
      | playwright_pytest | https://github.com/Jhonatanfc94/ |