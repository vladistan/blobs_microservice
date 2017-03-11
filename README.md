# Blob service

This is a very simple service useful to illustrate the concept of micro services. 

## Purpose

This service a simple cache for image files downloaded from 3rd party sites. This is useful
to improve responsiveness of web applications.

## Rest Methods

/blob/v1/count  -- displays how many times this method has been called by any client

/blob/v1/exists/URL/IDX -- checks if particular image exists in the service cache
     URL -- url of the remote image
     IDX -- usually 1
     
/blob/v1/obj/URL/IDX
     URL -- url of the remote image
     IDX -- usually 1
     
     GET  -- retrive the image
     POST -- store local copy of the image

