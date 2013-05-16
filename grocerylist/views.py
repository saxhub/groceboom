from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from grocerylist.models import Glist, Product, Aisle, Item, Store
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.contrib.auth.models import User, check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import logging
import json
log = logging.getLogger(__name__)

@login_required
def index(request):
    glists = Glist.objects.filter(owner_id = request.user.id)
    stores = Store.objects.filter(aisle__owner_id = request.user.id).distinct()
    context = {'glists' : glists, 'stores' : stores }
    return render(request, 'grocerylist/lists.html', context)


def login_page(request):
    return render(request, 'grocerylist/login.html')

def do_login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        # the password verified for the user
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')

        else:
            HttpResponse("The password is valid, but the account has been disabled!")
    else:
        # the authentication system was unable to verify the username and password
        HttpResponse("The username and password were incorrect.")

@login_required
def list_detail(request, glist_id):
    glist = get_object_or_404(Glist,pk=glist_id)
    if not request.user.has_perm('grocerylist.change_own_glist',glist):
        return HttpResponse('you don\'t have permission')
    else:
        product_options = Product.objects.filter(owner_id = glist.owner_id).exclude(glist = glist_id)
        store_items_query = glist.item_set.filter(product__aisles__store = glist.store)
        #order by product__aisle_sort doesn't work -- doesn't always use sort of active aisle.  would like to do without iterating
        store_items = {}
        for item in store_items_query:
            aisle = item.active_aisle()
            if store_items.get(aisle.sort) == None:
                store_items[aisle.sort] = {}
            if store_items[aisle.sort].get('aisle') == None:
                store_items[aisle.sort]['aisle'] = aisle
            if store_items[aisle.sort].get('items') == None:
                store_items[aisle.sort]['items'] = []
            store_items[aisle.sort]['items'].append(item)
        log.debug(store_items)
        notinstore_items = glist.item_set.exclude(product__aisles__store = glist.store)
        #all this store's aisles for select list
        aisles = Aisle.objects.filter(store = glist.store_id, owner_id = glist.owner_id).order_by('sort')
        if aisles.aggregate(Max('sort'))['sort__max'] == None: aisle_maxsort = 1
        else: aisle_maxsort = aisles.aggregate(Max('sort'))['sort__max']
        
        context = {'glist':glist, 'product_options':product_options, 'aisles':aisles, 'store_items' : store_items, 'notinstore_items' : notinstore_items, 'aisle_maxsort' : aisle_maxsort}
        return render (request, 'grocerylist/list_detail.html', context)

def save_list(request, glist_id):
    gl = get_object_or_404(Glist, pk=glist_id)
    aisle_maxsort = int(request.POST['aisle_maxsort']) + 1 
    for k,v in request.POST.iteritems():
        #if this is an aisle select for a not in store item
        if k[:13] == 'aisle_product':
            #strip out and store the product id from the end of the field name
            product_id = k[14:]
            #get the product object
            product_needs_aisle = Product.objects.get(pk=product_id)
            #this is the checkbox that tells whether to use the select or the new aisle input
            new_aisle_check_field = 'product_needs_aisle_' + product_id
            #if it's checked
            if request.POST.get(new_aisle_check_field):
                #this is the aisle name field for this product
                aisle_field = 'product_aisle_name_' + product_id
                if request.POST.get(aisle_field):
                    product_needs_aisle.aisles.create(name = request.POST[aisle_field], store_id = request.POST['store_id'], sort = aisle_maxsort, owner = gl.owner)
                aisle_maxsort += 1
            elif v:
                product_needs_aisle.aisles.add(v)

    if request.POST.get('new_product'):
    	new_product = Product(name = request.POST['new_product_name'], owner = gl.owner)
    	new_product.save()
        #new aisle
        if request.POST.get('new_product_needs_aisle'):
            new_product.aisles.create(name=request.POST['new_product_aisle_name'], store_id = request.POST['store_id'], sort = aisle_maxsort, owner = gl.owner)
            aisle_maxsort += 1
        #added to existing aisle
        else:
            new_product.aisles.add(request.POST['new_product_aisle'])
    	gl.item_set.create(product_id = new_product.id)
    elif request.POST.get('product'):
    	gl.item_set.create(product_id = request.POST['product'])
    
    return HttpResponseRedirect(reverse('list_detail', args=(gl.id,)))

def add_list(request):
    if request.POST.get('new_list_name') and request.POST.get('store_name'):
        store = Store(name = request.POST['store_name'])
        store.save()
        glist = Glist(name = request.POST['new_list_name'], owner = request.user, store = store)
        glist.save()
        return HttpResponseRedirect(reverse('list_detail', args=(glist.id,)))
    else:
        return HttpResponse('bruh, put in a dang name')


def serialize_aisles(request):
    for index, aisle_id in enumerate(request.POST.getlist('aisle[]')):
        a = Aisle.objects.get(pk=aisle_id)
        a.sort = index + 1
        a.save()
    return HttpResponse('')

def check_item(request):
    if request.POST.get('item_id'):
        item = Item.objects.get(pk=request.POST['item_id'])
        item.got_it = 1
        item.save()
    return HttpResponse(json.dumps(''), content_type="application/json")


def get_items(request, glist_id):
    glist = Glist.objects.get(pk=glist_id)
    store_items = glist.item_set.filter(product__aisles__store = glist.store).order_by('product__aisles__sort')
    template = loader.get_template('grocerylist/list_items.html')
    context = RequestContext(request, {
        'store_items': store_items,
    })
    output = template.render(context)
    return HttpResponse(json.dumps(output), content_type="application/json")

def get_aisles(request,store_id):
    aisles = Aisle.objects.filter(store = store_id).order_by('sort')
    template = loader.get_template('grocerylist/aisle_sort.html')
    context = RequestContext(request, {
        'aisles' : aisles,
    })
    return HttpResponse(json.dumps(template.render(context)), content_type="application/json")




