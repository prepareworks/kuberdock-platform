*** Settings ***
Documentation     A test suite containing tests related to login.

Resource          ./resource.robot

Suite Setup       Open Browser To Kuberdock Page
Suite Teardown    Close All Browsers

Test Teardown     Close All Error Messages
