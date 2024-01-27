import os
import shutil
from django.shortcuts import redirect, render
from django.http import HttpResponse
from deepface import DeepFace
from django.contrib import messages
from uuid import uuid4

def home(request):
    context = {
        'title' : "Home Page",
    }
    return render(request, 'home.html', context=context)


def facial_attribute_analysis(request):
    empty_directories("media/uploaded_images/", "media/other_images/")
    original_image_path = ''
    context = {
        'title' : 'DemoGraphic Attributes',
    }
    try:
        if request.method == 'POST':
            image_path = 'media/uploaded_images/'
            image_file = request.FILES.get('image') 
            print(image_file)
            
            if not image_file:
                messages.error(request, "Image file not found")
                return redirect('attribute-analysis')
            else:
                try:
                    image_path = os.path.join(image_path, image_file.name)
                    with open(image_path, 'wb') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                            
                    print(image_file)
                    demographic_attribute = DeepFace.analyze(img_path=image_path) 
                    emotions = demographic_attribute[0]['dominant_emotion']
                    age = demographic_attribute[0]['age']
                    gender = demographic_attribute[0]['dominant_gender']
                    race = demographic_attribute[0]['dominant_race']
                    
                    print(demographic_attribute)
                   
                    original_image_path = f'media/uploaded_images/{image_file.name}'
                    print(original_image_path)
                    context = {
                        'demographic_attribute': demographic_attribute,
                        'original_image_path': original_image_path,
                        'title' : "Success Page",
                        'dominant_emotion' : emotions,
                        'age' : age,
                        'gender' : gender,
                        'race' : race,
                    }
                    return render(request, 'success.html', context=context)
                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('attribute-analysis')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('attribute-analysis')
    return render(request, 'attribute_analysis.html', context=context)


# ------------------------------- Comparing Two Images ----------------------
def compare_images(request):
    original_image1_path = ''
    original_image2_path = ''
    
    empty_directories("media/uploaded_images/", "media/other_images/")

    context = {'title': 'Compare Faces'}

    try:
        if request.method == 'POST':
            image_path = 'media/uploaded_images/'
            image1_file = request.FILES.get('img1')
            image2_file = request.FILES.get('img2')

            if not image1_file or not image2_file:
                messages.error(request, "Image files not found")
                return redirect('compare-images')

            try:
                image1_path = os.path.join(image_path, image1_file.name)
                image2_path = os.path.join(image_path, image2_file.name)

                with open(image1_path, 'wb') as destination:
                    for chunk in image1_file.chunks():
                        destination.write(chunk)

                with open(image2_path, 'wb') as destination:
                    for chunk in image2_file.chunks():
                        destination.write(chunk)

                comparison = DeepFace.verify(img1_path=image1_path, img2_path=image2_path)
                verified_value = comparison['verified']
                difference = comparison['distance']
                
                print(comparison)
                print("Difference", difference)
                original_image1_path = f'media/uploaded_images/{image1_file.name}'
                original_image2_path = f'media/uploaded_images/{image2_file.name}'
                request.session['original_image1_path'] = original_image1_path

                print("First Image Path", original_image1_path)
                context = {
                    'result': comparison,
                    'original_image1_path': original_image1_path,
                    'original_image2_path': original_image2_path,
                    'verified' : verified_value,
                    'difference' : difference,
                }

                return render(request, "Image_comparison_success.html", context=context)

            except IOError as e:
                messages.error(request, "Error while processing images")
                return redirect('compare-images')

    except Exception as e:
        messages.error(request, str(e))
        return redirect('compare-images')

    return render(request, 'compare_images.html', context=context)


# -------------------------------- Face Verification from DB --------------------------------
def face_verification(request):
    empty_directories("media/uploaded_images/", "media/other_images/")
    result = ''
    found = False
    matched_images_paths = []
    if request.method == 'POST':
        user_image = request.FILES.get('user_image')
        other_images = request.FILES.getlist('other_images')

        # Save user image to the 'uploaded_images' folder
        user_image_path = os.path.join('media', 'uploaded_images', user_image.name)
        with open(user_image_path, 'wb') as user_image_file:
            for chunk in user_image.chunks():
                user_image_file.write(chunk)

        # Save other images to the 'other_images' folder
        other_images_folder = os.path.join('media', 'other_images')
        os.makedirs(other_images_folder, exist_ok=True)

        # Perform face recognition for each reference image
        for other_image in other_images:
            other_image_path = os.path.join(other_images_folder, other_image.name)
            with open(other_image_path, 'wb') as other_image_file:
                for chunk in other_image.chunks():
                    other_image_file.write(chunk)

        # Perform face recognition for each pair
        results = DeepFace.find(img_path=user_image_path, db_path=other_images_folder, enforce_detection=False)
        print("Results: ", results)
        
        # Getting Only Image Path of Selected Images 
        for result in results:
            matched_images_paths.extend(result['identity'].tolist())
            
        if len(matched_images_paths) > 0:
            found = True
        context = {
            'user_image_path': user_image_path, 
            'results' : results,
            'matched_images' : matched_images_paths,
            'images_found' : found,
        }
        return render(request, 'find-results.html', context=context)
    
    
    context = {'title': "Face Verification"}
    return render(request, 'face_verification.html', context=context)



def empty_directories(uploaded_images_path, other_images):
    shutil.rmtree(uploaded_images_path, ignore_errors=True)
    shutil.rmtree(other_images, ignore_errors=True)
    
    os.makedirs(uploaded_images_path, exist_ok=True)
    os.makedirs(other_images, exist_ok=True)
    
    return True