from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Pages, Refractiveindex, Extcoeff, Film, NewFilm
from scipy import interpolate
import numpy as np
import tmm as tmm


# Create your views here.

def index(request):
    #return HttpResponse("hello from optical parameter")
    # a = Film.objects.get(layer_sequence=id).delete()
    a = Film.objects.filter(layer_sequence__gt=1).delete()
    return render(request, 'optical_parameter/index.html', {
        'content':'This website is developed to play around the optical materials. You can explore the optical properties (e.g. refractive index, reflection) of common materials and establish your own simple optical films'
    })

# def materials(request):
#     material_inorganic = Pages.objects.all()
#     material_names = Pages.objects.values('book').distinct()
#     context = {
#         'Title':'All Materials',
#         'material_names':material_names,
#         'materials': material_inorganic,
#     }
#     return render(request,'optical_parameter/materials.html',context)

def materials(request):
    shelf_dict = {'Common Inorganic Material':'main','Organic Material':'organic','Glass': 'glass','Miscellaneous/Composite material':'other'}
    material_type = request.GET.get("materials_type")
    material_name = request.GET.get('materials_name')
    type = None
    if material_type is not None:
        type = shelf_dict[material_type]
        material_names = Pages.objects.filter(shelf= type).values('book').distinct()
        if material_name is not None:
            materials = Pages.objects.filter(book= material_name)
        else:
            materials = Pages.objects.filter(shelf= type)
    else:
        material_names = Pages.objects.values('book').distinct()
        # material_names = Pages.objects.all()
        if material_name is not None:
            materials = Pages.objects.filter(book= material_name)
        else:
            materials =Pages.objects.all()
    context = {
        'Title': 'All Materials',
        'material_type':type,
        'material_names': material_names,
        'materials': materials,
    }
    return render(request, 'optical_parameter/materials.html', context)

def details(request, id):
    assign_wave = request.GET.get("Wavelength")
    mat = Pages.objects.filter(pageid = id)
    mat_min = list(mat.values_list("rangeMin", flat=True))[0]*1000
    mat_max = list(mat.values_list("rangeMax", flat=True))[0]*1000
    mat_refractiveindex = Refractiveindex.objects.filter(pageid_id=id)
    mat_excoeff = Extcoeff.objects.filter(pageid_id=id)
    wave_r = list(mat_refractiveindex.values_list("wave", flat=True))
    wave_re = [i * 1000 for i in wave_r]
    n_re = list(mat_refractiveindex.values_list("refindex", flat=True))
    wave_e = list(mat_excoeff.values_list("wave", flat=True))
    wave_ex = [i * 1000 for i in wave_e]
    k_ex = list(mat_excoeff.values_list("coeff", flat=True))
    calculate_n = 0
    calculate_k = 0
    if len(wave_re)>0 and  assign_wave is not None:
        refractive_curve = interpolate.interp1d(wave_re, n_re, kind='quadratic')
        calculate_n = refractive_curve(assign_wave)
    if len(wave_ex)>0 and assign_wave is not None:
        excoeff_curve = interpolate.interp1d(wave_ex, k_ex, kind='quadratic')
        calculate_k = excoeff_curve(assign_wave)
    context = {
        'Material':mat,
        # 'Material': mat.values_list("page", flat=True),
        'Mat_min':mat_min,
        'Mat_max':mat_max,
        'Wave_re':wave_re,
        'N_re':n_re,
        'Wave_ex':wave_ex,
        'K_ex':k_ex,
        'Calculate_n': calculate_n,
        'Calculate_k': calculate_k,
    }
    return render(request, 'optical_parameter/details.html', context)

def film(request):
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    if request.method =='POST':
        form = NewFilm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/optical_parameter/film")
    else:
        form = NewFilm()
    context = {
        'Mat_form':form,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass':option_glass,
        'option_other':option_other,

    }
    return render(request, 'optical_parameter/film.html', context)

def testfilm(request):
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    print("point1")
    if request.method == 'POST':
        form = NewFilm(request.POST)
        # print(form.type, form.thickness, form.thickness)
        if form.is_valid():
            form.save()
            return redirect("/optical_parameter/design")
        else:
            print("not valid")
            messages.error(request, "Error")
    else:
        form = NewFilm()
    context = {
        'Mat_form':form,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass':option_glass,
        'option_other':option_other,

    }
    return render(request, 'optical_parameter/film.html', context)

def design(request):
    design = Film.objects.all()
    mat_type = list(design.values_list("type", flat=True))
    mat_mat = list(design.values_list("material", flat=True))
    mat_thick = [np.inf]
    mat_thickness = list(design.values_list("thickness", flat=True))
    mat_thick = mat_thick+mat_thickness+[np.inf]
    mat_layer = list(design.values_list("layer_sequence", flat=True))
    working_min = []
    working_max = []
    print(mat_type)
    print("------------")
    print(mat_mat)
    print("--------")
    print(mat_thick)
    print("--------")
    print(mat_layer)
    print("-----------")
    object = []
    refractives = []
    refrac_fns = []
    for i in range(0, len(mat_type)):
        objects = Pages.objects.filter(book=str(mat_mat[i]), hasextinction=1, hasrefractive=1).values_list("pageid", flat=True)
        print(objects[0])
        if objects is not None:
            object.append(objects[0])
            mat_refractiveindex = Refractiveindex.objects.filter(pageid_id=objects[0])
            mat_excoeff = Extcoeff.objects.filter(pageid_id=objects[0])
            wave_r = list(mat_refractiveindex.values_list("wave", flat=True))
            wave_re = [i * 1000 for i in wave_r]
            n_re = list(mat_refractiveindex.values_list("refindex", flat=True))
            wave_e = list(mat_excoeff.values_list("wave", flat=True))
            wave_ex = [i * 1000 for i in wave_e]
            k_ex = list(mat_excoeff.values_list("coeff", flat=True))
            refrac_element = []
            for wa in range(0, len(wave_re)):
                refrac_element.append([wave_re[wa], complex(n_re[wa],k_ex[wa])])
                # print(refrac_element)
            refrac_array = np.array(refrac_element)
            refractives.append(refrac_array)
            print("refractive element 0 is :----------------")
            # print(refrac_element[:,0])
            n_fn = interpolate.interp1d(refrac_array[:, 0].real, refrac_array[:, 1], kind='quadratic')
            print("range min", min(refrac_array[:, 0].real), "range max", max(refrac_array[:,0].real))
            # print("function result is",n_fn(400))
            refrac_fns.append(n_fn)
            working_min.append(min(refrac_array[:,0].real))
            working_max.append(max(refrac_array[:,0].real))
    working_range = [0,0]
    if len(working_max)>0:
        working_range = [max(working_min), min(working_max)]
    lamdas = list(np.linspace(working_range[0], working_range[1], 100))
    # initialize lists of y-values to plot
    Rnorm = []
    Tnorm = []
    d_list = mat_thick
    # R45 = []
    for lamda in lamdas:
        # For normal incidence, s and p polarizations are identical.
        # I arbitrarily decided to use 's'.
        n_list = [1]
        print("lamda is", lamda)
        for lay in range(0, len(mat_type)):
            # refrac_fn = refrac_fns[lay]
            print(lay)
            print(refrac_fns[lay])
            print(refrac_fns[lay](lamda))
            n_list.append(refrac_fns[lay](lamda))
        n_list.append(1)
        print(n_list)
        Rnorm.append(tmm.coh_tmm('s', n_list, d_list, 0, lamda)['R'])
        Tnorm.append(tmm.coh_tmm('s', n_list, d_list, 0, lamda)['T'])
    print("lamdas is", lamdas)
    print("R is", Rnorm)
    print("T is", Tnorm)
        # R45.append(unpolarized_RT(n_list, d_list, 45 * degree, 1 / k)['R'])
    context={
        'Design': design,
        'Wavelength':lamdas,
        'Reflectance':Rnorm,
        'Transmitance':Tnorm,
        'Working_range':working_range,
    }
    return render(request, 'optical_parameter/design.html', context)


def updatelayer(request, id):
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    a = Film.objects.get(layer_sequence=id)
    print(a)
    uform = NewFilm(instance=a)
    print("start the form")
    print(uform)
    print("end the form")
    if request.method == 'POST':
        uform = NewFilm(request.POST, instance=a)
        if uform.is_valid():
            uform.save()
            return redirect("/optical_parameter/design/")
    context = {
        'a': a,
        'uform':uform,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass':option_glass,
        'option_other':option_other,

    }
    return render(request, 'optical_parameter/layer_update.html', context)

def dellayer(request,id):
    a = Film.objects.get(layer_sequence=id).delete()
    return redirect("/optical_parameter/design/")