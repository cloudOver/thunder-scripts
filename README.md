This repository contains scripts for thunder parser - the automation tool for CoreCluster cloud.

# Script format and usage
* The format is not stable yet. Please follow this repository
Each line of script is one command. There is no possibility (yet) to divide lines or use backslashes inside them (new lines, etc.). The format is based on Dockerfile, but not 100% compatybile. Een not 50% compatybile.

By default, prototype of parser requires the `CORE_URL` and `CORE_TOKEN` environment variables to connect with cloud. All other environment variables, which starts with CORE_... are passed into scripts.

All other variables, required by scripts (`REQ_VAR` statement) should be passed to the parser as argument `VARABLE=value`.

All parameters of command could use quotes and double-quotes to deal with spaces in values.

# Commands
### SET variable value
Set variable's value. If variable was defined previously, it might be overwritten.
##### Example
```
SET IMAGE_URL http://domain.com/my_image_file.qcow2
```


### REQ_VAR variable:default_value
Require variable by script. If your script requires some specific variables (e.g. mysql root's pasword for mysql installation), it could require this by REQ_VAR command. Optionaly, you can pass the default value of variable, if it is not mandatory, but script uses it and variable could be overwritten.

All variables could be used futher in other commands. To access them use dolar sign followed by variable name (`$MY_VAR`).
##### Example
```
REQ_VAR VM_NAME
REQ_VAR VM_DESCRIPTION:'No description'
```


### APPEND variable value
Append value to previously defined variable. If variable was an integer, then try to add value. If variable was not defined, define new variable.
##### Example
```
SET IMAGE_URL http://domain.com/
APPEND IMAGE_URL my_image_file.qcow2
```


### APPENDL variable value
Append value as new line to previously defined variable. If variable was not defined, define new variable.
##### Example
```
SET MY_VAR 'first line'
APPENDL MY_VAR 'last line'
```


### CALL api:module:function param1=value param2=value ...
Call the CoreCluster API. First parameter is the function path divided by colons. Usually this is: *api*, *module*, *function*. Each function called in this way should accept token authorization.

All following parameters of CALL are treated as parameters to the function. Each parameter is colon-separated pair:
* parameter name
* parameter value
As the parameter's value you can use variables defined by *SET* or required by *REQ_VAR*.
##### Example:
```
CALL api:vm:create template_id:$TEMPLATE_ID base_image_id:$IMAGE_ID name:$VM_NAME description:$VM_DESCRIPTION
```


### REQUIRE script_name
Load another script from repository. This allows to re-use predefined tools to speed up your work. Required script gets all variables defined by SET, APPEND or APPENDL.
##### Example
This image uses another script from repository - image-upload. Only task in this script is to set proper variables.
```
SET IMAGE_NAME 'Debian Jessie'
SET IMAGE_DESCRIPTION 'Debian 8.x Cloud'
SET IMAGE_TYPE 'transient'
SET IMAGE_URL 'http://cdimage.debian.org/cdimage/openstack/current/debian-8.5.0-openstack-amd64.qcow2'
SET IMAGE_FORMAT 'qcow2'

REQUIRE image-upload
```


### DONE core_module:field:value
Check wether the required by script resource is present. If so, then stop execution of script (it doesn't trigger higher level of scripts, in case when script was loaded by *REQUIRE*).

`DONE` calls the get_list function of given api module. This returns list of dictionaries describing resource (for example: api/vm/get_list returns list of dicrionaries with details of VMs). If any item of returned list has field given as *field* and its value equals to *value*, then script execution is stopped.
#####Example
```
REQ_VAR IMAGE_NAME
REQ_VAR IMAGE_DESCRIPTION:'No description'
REQ_VAR IMAGE_DISK_CONTROLLER:'virtio'
REQ_VAR IMAGE_SIZE
REQ_VAR IMAGE_TYPE

DONE image:name:$IMAGE_NAME
CALL api:image:create size:$IMAGE_SIZE image_type:$IMAGE_TYPE name:$IMAGE_NAME description:$IMAGE_DESCRIPTION disk_controller:$IMAGE_DISK_CONTROLLER
```

### RESOURCE api_module:field:value AS VARIABLE:field
This works similar to the DONE, but if given resource is found in CoreCluster's api module (e.g. /api/vm/get_list returns VM with name="abc"), the result is stored in given after AS parameter variable.
##### Example
To get id of template defined by name (TEMPLATE_NAME variable), we need to get list of templates and find one with name equal to $TEMPLATE_NAME. Then we want to store id of this template as TEMPLATE_ID variable. Later, this variable could be used to launch VM with this template.
```
REQ_VAR TEMPLATE_NAME
RESOURCE template:name:$TEMPLATE_NAME AS TEMPLATE_ID:id
```

### RAISE reason
Finish all scripts with error. This may me used when something is going wrong, or resource is not present.
##### Example
```
REQ_VAR TEMPLATE_NAME

DONE template:name:$TEMPLATE_NAME
RAISE 'Template not found'
```
