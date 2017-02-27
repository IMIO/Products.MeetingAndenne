function getMultiSelectContent(rq, params) {
  /* Gets the content of a rich text field before sending it through an Ajax
     request. */
  var fieldName = rq.hook.split('_')[1];
  var formId = 'ajax_edit_' + fieldName;
  var theForm = document.getElementById(formId);
  var theWidget = theForm[fieldName];

  valueData = "(";
  for (var i = 0; i < theWidget.options.length; i++)
    if (theWidget.options[i].selected)
      valueData= valueData + theWidget.options[i].value + ",";

  valueData= valueData +")";
  /* Disable the Plone automatic detection of changes to the form. Indeed,
     Plone is not aware that we have sent the form, so he will try to display
     a message, saying that changes will be lost because an unsubmitted form
     contains changed data. */
  window.onbeforeunload = null;
  // Construct parameters and return them.
  var params = "&fieldName=" + encodeURIComponent(fieldName) +
               '&fieldContent=' + encodeURIComponent(valueData);
  return params
}

function welcomeNowUser(itemUrl, userId, actionType){
  if (actionType == "delete") {
    if (confirm(are_you_sure)) {
      var params = {'action': 'WelcomeNowPerson', 'userId': userId, 'actionType': actionType};
      askAjaxChunk('meeting_users_', 'POST', itemUrl, '@@ma-macros', 'itemPeople', params);
    }
  }
  else 
  {
    var params = {'action': 'WelcomeNowPerson', 'userId': userId, 'actionType': actionType};
    askAjaxChunk('meeting_users_', 'POST', itemUrl, '@@ma-macros', 'itemPeople', params);

  }
}

function welcomeUserAndenne(itemUrl, userId, action){
  if (confirm(are_you_sure)) {
    var params = {'action': 'WelcomePerson', 'userId': userId, 'actionType': action};
    askAjaxChunk('meeting_users_', 'POST', itemUrl, '@@ma-macros', 'itemPeople', params);
  }
}

function confirmByebyeUserAndenne(itemUrl, userId, actionType, byeType){
  dialogData = {'action': 'ByebyePerson', 'itemUrl': itemUrl,
                'userId': userId, 'actionType': actionType, 'byeType':byeType};
  if (actionType == "delete") {
    if (confirm(are_you_sure)) {
      delete dialogData['itemUrl'];
      askAjaxChunk('meeting_users_', 'POST', itemUrl, '@@ma-macros', 'itemPeople', dialogData);
    }
  }
  else openDialog('confirmByebyeUser');
}
