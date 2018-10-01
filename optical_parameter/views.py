from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Pages, Refractiveindex, Extcoeff, Film, NewFilm
from scipy import interpolate
import numpy as np
import tmm as tmm
import math as math


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
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    shelf_dict = {'Common Inorganic Materials':'main','Organic Materials':'organic','Glass': 'glass','Miscellaneous and Composite materials':'other'}
    material_type = request.GET.get("type")
    print('Materials Type is:',material_type)
    material_name = request.GET.get('material')
    print('Materials name is:',material_name)
    type = None
    if material_type != None:
        type = shelf_dict[material_type]
        material_names = Pages.objects.filter(shelf= type).values('book').distinct()
        if material_name is not None and material_name != "-----":
            materials = Pages.objects.filter(book= material_name)
        else:
            materials = Pages.objects.filter(shelf= type)
    else:
            materials =Pages.objects.all()
    context = {
        'Title': 'All Materials',
        'material_type':type,
        # 'material_names': material_names,
        'materials': materials,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass': option_glass,
        'option_other': option_other,
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
    # n_air = [1 for number in range(len(n_re))]

    incident_angle = request.GET.get("Incident_angle")
    incident_angle_radians = 0
    if incident_angle != None:
        incident_angle_radians = math.radians(float(incident_angle))
    reflec_s = []
    reflec_p = []
    trans_s = []
    trans_p = []
    for i in range(len(n_re)):
        th_f = tmm.snell(1, n_re[i], incident_angle_radians)
        reflec_s.append(tmm.interface_R("s", 1, n_re[i], incident_angle_radians, th_f).real)
        reflec_p.append(tmm.interface_R("p", 1, n_re[i], incident_angle_radians, th_f).real)
        trans_s.append(tmm.interface_T("s", 1, n_re[i], incident_angle_radians, th_f).real)
        trans_p.append(tmm.interface_T("p", 1, n_re[i], incident_angle_radians, th_f).real)
    context = {
        'Material':list(mat.values_list("book", flat=True))[0],
        'Material_page': list(mat.values_list("page", flat=True))[0],
        'Mat_min':mat_min,
        'Mat_max':mat_max,
        'Wave_re':wave_re,
        'N_re':n_re,
        'Wave_ex':wave_ex,
        'K_ex':k_ex,
        'Calculate_n': calculate_n,
        'Calculate_k': calculate_k,
        'Reflection_s':reflec_s,
        'Reflection_p': reflec_p,
        'Transmission_s':trans_s,
        'Transmission_p':trans_p,
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
    incident_angle = request.GET.get("Incident_angle")
    incident_angle_radians = 0
    if incident_angle != None:
        incident_angle_radians = math.radians(float(incident_angle))
    if incident_angle == None:
        incident_angle = 0
    lamda_poynting  = request.GET.get("lamda_poynting")
    if lamda_poynting == None:
        lamda_poynting = 400
    design = Film.objects.all()
    mat_type = list(design.values_list("type", flat=True))
    mat_mat = list(design.values_list("material", flat=True))
    mat_thick = [np.inf]
    mat_thickness = list(design.values_list("thickness", flat=True))
    mat_thick = mat_thick+mat_thickness+[np.inf]
    mat_layer = list(design.values_list("layer_sequence", flat=True))
    working_min = []
    working_max = []
    # print(mat_type)
    # print("------------")
    # print(mat_mat)
    # print("--------")
    # print(mat_thick)
    # print("--------")
    # print(mat_layer)
    # print("-----------")
    object = []
    refractives = []
    refrac_fns = []
    for i in range(0, len(mat_type)):
        objects = Pages.objects.filter(book=str(mat_mat[i]), hasextinction=1, hasrefractive=1).values_list("pageid", flat=True)
        # print(objects[0])
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
            # print("refractive element 0 is :----------------")
            # print(refrac_element[:,0])
            n_fn = interpolate.interp1d(refrac_array[:, 0].real, refrac_array[:, 1], kind='quadratic')
            # print("range min", min(refrac_array[:, 0].real), "range max", max(refrac_array[:,0].real))
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
        # print("lamda is", lamda)
        for lay in range(0, len(mat_type)):
            # refrac_fn = refrac_fns[lay]
            # print(lay)
            # print(refrac_fns[lay])
            # print(refrac_fns[lay](lamda))
            n_list.append(refrac_fns[lay](lamda))
        n_list.append(1)
        # print(n_list)
        Rnorm.append(tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda)['R'])
        Tnorm.append(tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda)['T'])
    # th_0 = pi / 4
    # lam_vac = 400
    # pol = 'p'
    coh_tmm_data_s = tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda_poynting)
    coh_tmm_data_p = tmm.coh_tmm('p', n_list, d_list, incident_angle_radians, lamda_poynting)
    ds = np.linspace(0, sum(d_list[1:-1]) , num=100)
    print(sum(d_list[1:-1]))
    poyn = []
    absor = []
    for d in ds:
        layer, d_in_layer = tmm.find_in_structure_with_inf(d_list, d)
        data = tmm.position_resolved(layer, d_in_layer, coh_tmm_data_s)
        poyn.append(data['poyn'])
        absor.append(data['absor'])
    ds = list(ds)
    # convert data to numpy arrays for easy scaling in the plot
    # poyn = np.array(poyn)
    # absor = np.array(absor)
    # print(ds.shape)
    # print(poyn.shape)
    print(absor)
    # print("lamdas is", lamdas)
    # print("R is", Rnorm)
    # print("T is", Tnorm)
        # R45.append(unpolarized_RT(n_list, d_list, 45 * degree, 1 / k)['R'])
    context={
        'Design': design,
        'Wavelength':lamdas,
        'Reflectance':Rnorm,
        'Transmitance':Tnorm,
        'Working_range':working_range,
        'Angle': incident_angle,
        'Absorption': absor,
        'Ponyting': poyn,
        'Depth':ds,
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

def visualize(request):
    return render(request, 'optical_parameter/visualization.html', {
        'content':'Here we visualize major measured data (refractive index) in different ranges'
    })