from django.shortcuts import render
from django.conf import settings
import os
import sys
sys.path.append('.\Fingerprint')

import predict


def home(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
         
        # Tạo đường dẫn tới file ảnh đã được upload
        image_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        # Lưu file vào thư mục lưu trữ
        with open(image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Tạo đường dẫn URL tới ảnh
        image_url = os.path.join(settings.MEDIA_URL, uploaded_file.name)

        if image_path is not None:
            image_result , score = predict.predict(image_path)
            print("ket qua la : ",image_result)
            print("điểm: ", score)
            
            if score!= None:
                if score < 0.02:
                    score = None
                else:
                    score = score*100
            
          
            if image_result  != None and score!=None:
                path_result = os.path.join(settings.IMG_URL, image_result)
            else:
                if score == None:
                    path_result = os.path.join(settings.IMG_URL, "search-no-result-concept-illustration-flat-design-eps10-modern-graphic-element-for-landing-page-empty-state-ui-infographic-icon-vector.jpg")
         
        # Truyền đường dẫn ảnh vào context
        context = {'upload_success': True, 'image_url': image_url, 'path_result': path_result, "score": score}
         
        return render(request, 'home.html', context)
     
    return render(request, 'home.html')
