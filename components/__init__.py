def access_denied(request):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.7/dist/tailwind.min.css" rel="stylesheet">
    <title>Access Denied</title>
    <style>
        body {{
            background-color: #f4f4f4;
        }}
    </style>
</head>
<body class="flex items-center justify-center min-h-screen">
    <div class="max-w-md p-8 bg-white rounded-lg shadow-lg">
        <div class="text-center">
            <svg class="w-12 h-12 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <h1 class="text-2xl font-semibold mt-4">Access Denied</h1>
            <p class="text-gray-600 mt-2">You do not have permission to access this content.</p>
        </div>
        
        <form class="mt-6" action="{request.path}" method="post">
            <label for="pin" class="block text-gray-700 font-semibold mb-2">Please enter your PIN:</label>
            <input type="password" id="pin" name="pin" class="w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-300 focus:border-blue-500">
            
            <button type="submit" class="mt-6 w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring focus:ring-blue-300">
                Submit
            </button>
        </form>
        
        <p class="mt-6 text-center text-gray-500 text-sm">
            If you believe this is a mistake, please contact the administrator for assistance.
        </p>
    </div>
</body>
</html>
'''

def pin_error(request):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.7/dist/tailwind.min.css" rel="stylesheet">
    <title>Access Denied</title>
    <style>
        body {{
            background-color: #f4f4f4;
        }}
    </style>
</head>
<body class="flex items-center justify-center min-h-screen">
    <div class="max-w-md p-8 bg-white rounded-lg shadow-lg">
        <div class="text-center">
            <svg class="w-12 h-12 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <h1 class="text-2xl font-semibold mt-4">Access Denied</h1>
            <p class="text-gray-600 mt-2">You do not have permission to access this content.</p>
        </div>

        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-6" role="alert">
            <strong class="font-bold">Alert!</strong>
            <span class="block sm:inline">Incorrect pin.</span>
            <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
                <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849c-.195.195-.512.195-.707 0L10 10.707l-3.646 3.646a.5.5 0 01-.708 0l-.708-.707a.5.5 0 010-.708L8.293 10 4.646 6.354a.5.5 0 010-.708l.708-.708a.5.5 0 01.708 0L10 9.293l3.646-3.647a.5.5 0 01.708 0l.708.708a.5.5 0 010 .708L11.707 10l3.647 3.646a.5.5 0 010 .708l-.707.707z"/></svg>
            </span>
        </div>
        
        <form class="mt-6" action="{request.path}" method="post">
            <label for="pin" class="block text-gray-700 font-semibold mb-2">Please enter your PIN:</label>
            <input type="password" id="pin" name="pin" class="w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-300 focus:border-blue-500">
            
            <button type="submit" class="mt-6 w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring focus:ring-blue-300">
                Submit
            </button>
        </form>
        
        <p class="mt-6 text-center text-gray-500 text-sm">
            If you believe this is a mistake, please contact the administrator for assistance.
        </p>
    </div>
</body>
</html>
'''
