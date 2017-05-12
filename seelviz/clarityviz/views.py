from django.views import generic
from .models import Compute, Plot
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render_to_response
from django.template import RequestContext

class LogView(generic.ListView):
  template_name = 'clarityviz/log.html'
  context_object_name = 'all_computes'

  def get_queryset(self):
      return Compute.objects.all()


class OutputView(generic.DetailView):
    model = Compute
    template_name = 'clarityviz/output.html'

    def get(self, request, *args, **kwargs):
        primary_key = self.kwargs['pk']
        query_set = Compute.objects.filter(pk=primary_key)
        for compute in query_set:
            new_compute = compute

        print(new_compute.token)
        token = ''
        # if not new_compute.token.endswith('reorient_atlas'):
        #     token = new_compute.token + 'reorient_atlas'
        # else:
        #     token = new_compute.token
        token = new_compute.token

        plotly_files = []
        all_files = []
        for filepath in glob.glob('output/' + token + '/*'):
            absPath = os.path.abspath(filepath)
            if not os.path.isdir(absPath):
                filename = filepath.split('/')[2]
                all_files.append(filename)
                if filepath.endswith('html'):
                    plotly_files.append(filename)
        # context = {'token': token, 'all_files': all_files, 'plotly_files': plotly_files}

        context = locals()
        context['token'] = token
        context['all_files'] = all_files
        context['plotly_files'] = plotly_files
        context['html'] = 'html'
        return render(request, self.template_name, context)
        # return render_to_response(self.template_name, context, context_instance=RequestContext(request))


class ComputeCreate(CreateView):
    model = Compute
    fields = ['token', 'bucket', 'num_points']

    def form_valid(self, form):

        token = form.cleaned_data['token']
        bucket = form.cleaned_data['bucket']
        num_points = form.cleaned_data['num_points']

        num_results = Compute.objects.filter(token=token).count()

        if num_results == 0:
            # if the token is not already in the db, just add it.
            self.object = form.save()
        else:
            # if the token is already in the db, delete the old one and save the new one.
            Compute.objects.filter(token=token).delete()
            self.object = form.save()

        token_compute(token, bucket, num_points)
        print('meme token')
        print(token)

        return super(ComputeCreate, self).form_valid(form)

class PlotView(generic.DetailView):
    model = Plot
    template_name = 'clarityviz/plot.html'



# =============================================


from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
# from django.template import loader
from django.http import HttpResponse
from .models import Compute

# non django stuff ========

import os
import os.path

import shutil
import tempfile
import glob
import random

from numpy import genfromtxt

import time

from subprocess import Popen, PIPE
import sys

def index(request):
    # return HttpResponse("<h2>Hello World</h2>")

    # get token from user form, then pass that token into the url 
    # while running the pipeline, then open the link to the output 
    # with the token e.g. /clarityviz/fear199

    # template = loader.get_template('clarityviz/index.html')

    # return HttpResponse(template.render(context, request))

    # uploads = TokenUpload.objects.all()
    # context = {'uploads': uploads}

    # if(request.GET.get('tokenButton')):
    #     test.testFunction( request.GET.get('myToken') )
    return render(request, 'clarityviz/index.html')
    # return render(request, 'clarityviz/index.html', context)


def log(request):
    all_computes = Compute.objects.all()
    context = {
        'all_computes': all_computes,
    }
    return render(request, 'clarityviz/log.html', context)

def test_function():
    print('TEST FUNCTION')

def execute_cmd(cmd):
    """
    Given a bash command, it is executed and the response piped back to the
    calling script
    """
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    code = p.returncode
    if code:
        sys.exit("Error  " + str(code) + ": " + err)
    return out, err


# def token_compute(request):
#     print('INSIDE TOKEN_COMPUTE')
#     token = request.POST['token']
def token_compute(token, bucket, num_points=10000):
    print('INSIDE TOKEN_COMPUTE')

    cmd_template = 'python create_job.py --bucket {0} --credentials accessKeys.csv --token {1}'
    cmd = cmd_template.format(bucket, token)
    out, err = execute_cmd(cmd)




def plot(request, file_info):

    token = file_info.split('/')[0]
    type = file_info.split('/')[1]
    plot_type = ''
    description = ''
    file_name = ''
    if type == 'brain':
        plot_type = 'Brain Pointcloud'
        description = 'In the plot above we have a point cloud visualization of the 10,000 brightest points of the CLARITY brain selected after image filtering and histogram equalization.  The filtering and histogram equalization increased the relative contrast of each voxel relative to its nearest neighbors; the 10,000 brightest points were selected by randomly sampling voxels with 255 grey scale values.  We hypothesize that the denser areas of the point cloud correspond to brain regions with the more neurological activity.'
        file_name = token + '_brain_pointcloud.html'
    elif type == 'edgecount':
        plot_type = 'Edge Count Pointcloud'
        description = '''This purple node and cyan edge plot shows the connections from the density plot.  Each cyan edge was drawn with the same epsilon ball initialization used for the density plot.  It's important to note that the process of finding all the edges for a given node is a significant computational task that scales exponentially with increased epsilon ball radius.  The most connected nodes may show some properties of interest'''
        file_name = token + '_edge_count_pointcloud.html'
    elif type == 'density':
        plot_type = 'Density Pointcloud'
        description = 'The multicolored plot shows a false-coloration scheme of the 10,000 brightest points by their edge counts, relative to a preselected epsilon ball radius.  The epsilon ball radius determines the number of edges a given node has by connecting all neighboring nodes within the radius with an edge.  Black nodes had an edge count of 0.  Then, in reverse rainbow order, (purple to red), we get increasing numbers of edges.  The densest node with the most edges is shown in white.  The plot supports up to 20 different colors.'
        file_name = token + '_density_pointcloud.html'
    elif type == 'densityheatmap':
        plot_type = 'Density Pointcloud Heatmap'
        file_name = token + '_density_pointcloud_heatmap.html'
    elif type == 'atlasregion':
        plot_type = 'Atlas Region Pointcloud'
        description = 'This graph shows a plot of the brain with each region as designated by the atlas a unique colored. Controls along the side allow for toggling the traces on/off'
        file_name = token + '_region_pointcloud.html'

    path = '/root/clvizdjango/seelviz/output/' + token +'/' + file_name
    html = """
    {% extends "clarityviz/header.html" %}

    {% block content %}

    <header>
        <div class="header-content">
            <div class="header-content-inner">
                {% if type %}
                    <h1>{{type}}</h2>
                {% endif %}
            </div>
        </div>
    </header>

    <body>

    <section class="bg-graph" id="about">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 col-lg-offset-2 text-center">
    """

    with open(path, "r") as ins:
        for line in ins:
            html += line

    html += """
                </div>
            </div>
        </div>
        <div class="container">
            {% if description %}
                <p>{{description}}</p>
            {% endif %}
        </div>
    </section>
    </body>
    </html>
    {% endblock %}
    """

    with open("clarityviz/templates/clarityviz/plot.html", "w+") as text_file:
        text_file.write("{}".format(html))


    context = {'type': plot_type, 'description': description}

    return render(request, 'clarityviz/plot.html', context)


def output(request, token):
    return render(request, 'clarityviz/output.html')

