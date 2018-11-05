from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Pages, Refractiveindex, Extcoeff, Film, NewFilm, OptimalFilmDesign, FormOptimalFilmDesign
from scipy import interpolate
import numpy as np
import tmm as tmm
import math as math
from .classes import OpticalMaterial
from .optimization import optimizedesign

# Create your views here.

def index(request):
    a = Film.objects.filter(layer_sequence__gt=1).delete()
    return render(request, 'optical_parameter/index.html', {
        'content':'This website is developed to play around the optical materials. You can explore the optical properties (e.g. refractive index, reflection) of common materials and establish your own simple optical films'
    })


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
        'materials': materials,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass': option_glass,
        'option_other': option_other,
    }
    return render(request, 'optical_parameter/materials.html', context)

# the function corresponding to showing detailed optical properties of selected materials
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
    if request.method == 'POST':
        form = NewFilm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect("/optical_parameter/design")
        else:
            # print("not valid")
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

# the function corresponding to the simulation result of the designed optical film
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
    object = []
    refractives = []
    refrac_fns = []
    miss_ex_mats = []
    for i in range(0, len(mat_type)):
        results = Pages.objects.filter(book=str(mat_mat[i]), hasrefractive=1, hasextinction = 1).values_list("pageid", flat=True)
        # print('objects is', objects)
        if results.exists():
            objects = results
        else:
            objects = Pages.objects.filter(book=str(mat_mat[i]), hasrefractive=1).values_list("pageid", flat=True)
        if objects.exists():
            object.append(objects[0])
            mat_refractiveindex = Refractiveindex.objects.filter(pageid_id=objects[0])
            mat_excoeff = Extcoeff.objects.filter(pageid_id=objects[0])
            wave_r = list(mat_refractiveindex.values_list("wave", flat=True))
            wave_re = [i * 1000 for i in wave_r]
            n_re = list(mat_refractiveindex.values_list("refindex", flat=True))
            wave_e = list(mat_excoeff.values_list("wave", flat=True))
            wave_ex = [i * 1000 for i in wave_e]
            k_ex = [0.000000001]*len(wave_re)
            if mat_excoeff.exists():
                k_ex = list(mat_excoeff.values_list("coeff", flat=True))
            else:
                miss_ex_mats.append(list(Pages.objects.filter(pageid = objects[0]).values_list("book", flat=True))[0])
            refrac_element = []
            for wa in range(0, len(wave_re)):
                refrac_element.append([wave_re[wa], complex(n_re[wa],k_ex[wa])])
                # print(refrac_element)
            refrac_array = np.array(refrac_element)
            refractives.append(refrac_array)
            n_fn = interpolate.interp1d(refrac_array[:, 0].real, refrac_array[:, 1], kind='quadratic')
            refrac_fns.append(n_fn)
            working_min.append(min(refrac_array[:,0].real))
            working_max.append(max(refrac_array[:,0].real))
    working_range = [0,0]
    if len(working_max)>0:
        working_range = [max(working_min), min(working_max)]
    lamdas = list(np.linspace(working_range[0], working_range[1], 100))
    Rnorm = []
    Tnorm = []
    d_list = mat_thick
    for lamda in lamdas:
        # For normal incidence, s and p polarizations are identical.
        # I arbitrarily decided to use 's'.
        n_list = [1]
        for lay in range(0, len(mat_type)):
            n_list.append(refrac_fns[lay](lamda))
        n_list.append(1)
        Rnorm.append(tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda)['R'])
        Tnorm.append(tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda)['T'])

    coh_tmm_data_s = tmm.coh_tmm('s', n_list, d_list, incident_angle_radians, lamda_poynting)
    coh_tmm_data_p = tmm.coh_tmm('p', n_list, d_list, incident_angle_radians, lamda_poynting)
    ds = np.linspace(0, sum(d_list[1:-1]) , num=100)
    poyn = []
    absor = []
    for d in ds:
        layer, d_in_layer = tmm.find_in_structure_with_inf(d_list, d)
        data = tmm.position_resolved(layer, d_in_layer, coh_tmm_data_s)
        poyn.append(data['poyn'])
        absor.append(data['absor'])
    ds = list(ds)
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
        'Miss_ex_mat':miss_ex_mats,
    }
    print('test', tmm.coh_tmm('s', [1, 1.3, 1.95, 2.25], [np.inf, 100, 66.67, np.inf], 0, 520)['R'])
    return render(request, 'optical_parameter/design.html', context)


def updatelayer(request, id):
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    a = Film.objects.get(layer_sequence=id)
    uform = NewFilm(instance=a)
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
        'content':'Here we visualize major measured data in different ranges'
    })


def optimalfilm(request):
    option_main = list(Pages.objects.filter(shelf="main").values_list("book", flat=True).distinct())
    option_organic = list(Pages.objects.filter(shelf="organic").values_list("book", flat=True).distinct())
    option_glass = list(Pages.objects.filter(shelf="glass").values_list("book", flat=True).distinct())
    option_other = list(Pages.objects.filter(shelf="other").values_list("book", flat=True).distinct())
    if request.method =='POST':
        form = FormOptimalFilmDesign(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect("/optimal/list/")
        else:
            # print("not valid")
            messages.error(request, "Error")
    else:
        form = FormOptimalFilmDesign()
    context = {
        'Mat_form':form,
        'option_main': option_main,
        'option_organic': option_organic,
        'option_glass':option_glass,
        'option_other':option_other,

    }
    return render(request, 'optical_parameter/optimalfilm.html', context)

def optimallist(request):
    design = OptimalFilmDesign.objects.all()
    print(design)
    context = {
        'design':design,
    }
    return render(request, 'optical_parameter/optimalfilmlist.html', context)

def deloptimaldesign(request,id):
    a = OptimalFilmDesign.objects.get(id=id).delete()
    return redirect("/optimal/list/")


# according to the design boundaries including the types of materials, total film thickness, and the target functions, this function can optimize the design accordingly.
def calculateoptimaldesign(request, id):

    # design_condition = {'substrate':None, 'coat_material', 'minrange', 'maxrange', 'maxthickness', 'goal'}
    design_condition = {}

    coat_mat = []
    coat_mat_id = []
    working_min = list(OptimalFilmDesign.objects.filter(id=id).values_list("wave_min", flat=True))
    working_max = list(OptimalFilmDesign.objects.filter(id=id).values_list("wave_max", flat=True))
    plot_min = [working_min[0]-100]
    plot_max = [working_max[0]+100]


    for i in range(1,5):
        mat = list(OptimalFilmDesign.objects.filter(id=id).values_list("material_%d" % (i), flat=True))[0]
        search = Pages.objects.filter(book=mat, hasrefractive=1, hasextinction = 1, rangeMax__gte=working_max[0]/1000, rangeMin__lte=working_min[0]/1000).values_list("pageid", flat=True)
        if search.exists():
            mat_id = search
        else:
            mat_id = Pages.objects.filter(book=mat, hasrefractive=1, rangeMax__gte=working_max[0]/1000, rangeMin__lte=working_min[0]/1000).values_list("pageid", flat=True)
        # coat_mat.append(mat)
        if mat_id.exists():
            coat_mat_id.append(list(mat_id)[0])
        coat_mat_id = list(set(coat_mat_id))


    for m in range(len(coat_mat_id)):
        new = OpticalMaterial(coat_mat_id[m])
        new.get_refractives()
        coat_mat.append(new)
        working_min.append(new.minwave)
        working_max.append(new.maxwave)
        plot_min.append(new.minwave)
        plot_max.append(new.maxwave)

    sub_mat_name = list(OptimalFilmDesign.objects.filter(id=id).values_list("material_substrate", flat=True))[0]
    search_sub = Pages.objects.filter(book=sub_mat_name, hasrefractive=1, hasextinction=1).values_list("pageid", flat=True)
    if search_sub.exists():
        substrate_mat_id = list(search_sub)[0]
    else:
        substrate_mat_id = list(Pages.objects.filter(book=sub_mat, hasrefractive=1).values_list("pageid", flat=True))[0]

    substrate = OpticalMaterial(substrate_mat_id)
    substrate.get_refractives()
    working_min.append(substrate.minwave)
    working_max.append(substrate.maxwave)
    plot_min.append(substrate.minwave)
    plot_max.append(substrate.maxwave)
    design_condition['substrate'] = substrate
    design_condition['coat_material'] = coat_mat
    design_condition['minrange'] = max(working_min)
    design_condition['maxrange'] = min(working_max)
    design_condition['maxthickness'] = list(OptimalFilmDesign.objects.filter(id=id).values_list("max_thickness", flat=True))[0]
    design_condition['goal'] = list(OptimalFilmDesign.objects.filter(id=id).values_list("filmtype", flat=True))[0]

    best_design = optimizedesign(design_condition['substrate'],design_condition['coat_material'],design_condition['minrange'], design_condition['maxrange'], design_condition['maxthickness'], design_condition['goal'])

    if best_design != None:
        best_coatings = best_design[0]
        best_ds = best_design[1][0][0]
        best_reflection = best_design[2][0]
        plot_min = max(plot_min)
        plot_max = min(plot_max)
        lamdas = list(np.linspace(plot_min, plot_max, num = 100))
        coating_complex_functions = []
        best_coatings_names = []
        for i in range(len(best_coatings)):
            function = best_coatings[i].get_complex_function()
            coating_complex_functions.append(function)
            best_coatings_names.append(best_coatings[i].name)
        substrate_complex_function = substrate.get_complex_function()

        plot_reflection = []
        plot_transmission = []
        for wa in lamdas:
            refractive_element = [1]
            for k in range(len(coating_complex_functions)):
                # print(coating_refractive_functions[i](medium_wavelength))
                refractive_element.append(coating_complex_functions[k](wa))
            refractive_element.append(substrate_complex_function(wa))

            # print(refractive_element)
            plot_reflection.append(tmm.coh_tmm('s', refractive_element, best_ds.tolist(), 0, wa)['R'])
            plot_transmission.append(tmm.coh_tmm('s', refractive_element, best_ds.tolist(), 0, wa)['T'])
        coating_thickness_lib = []
        for ele in range(len(best_coatings_names)):
            element = {}
            element['order'] = ele+1
            element['name'] = best_coatings_names[ele]
            element['thickness'] = best_ds[ele+1]
            coating_thickness_lib.append(element)

    else:
        best_coatings = None
        best_ds = None
        best_reflection = None
        best_coatings_names = None
        lamdas = None
        plot_reflection = None
        plot_transmission = None
        coating_thickness_lib = []


    coating_materials = Pages.objects.filter(pageid__in=coat_mat_id)
    substrate_material = Pages.objects.filter(pageid=substrate_mat_id)

    context = {
        'coat_mat': coating_materials,
        'substrate_mat': substrate_material,
        'design_condition': design_condition,
        'plot_wave':lamdas,
        'plot_reflection':plot_reflection,
        'plot_transmission':plot_transmission,
        'best_coating_name':best_coatings_names,
        'best_design_thickness':best_ds,
        'best_design_coatings':coating_thickness_lib,
        'best_reflectance':best_reflection,
    }
    return render(request, 'optical_parameter/calculateoptimalfilm.html', context)
