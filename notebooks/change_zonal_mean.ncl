;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Multi-plot of zonal means
; AR6 - WGI - Chapter8 - Stéphane Sénési - 09/2019-03/2021
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


; Read nx*ny files, each having 6 1d-fields representing zonal means and which names are
;      pctl5   =varname+"_pctl5"
;      pctl95  =varname+"_pctl95"
;      variab5 =varname+"_variab5"
;      variab95=varname+"_variab95"
;      mean=varname+"_mean"
;      land_mean=varname+"_land_mean"
; with varname == either "pr" or "P-E"

; plot mean as a solid colored line and land_mean as a dashed one

; plot a light colored transparent shade between pctl5 and pctl95, and
;  a darker one between variab5 and variab95.

; The choosen color is distinct for each line , and matches CMIP6 SSP
;  colors if lines match ssp126, ssp245 and ssp585

; General, lines and columns titles can be set by args

; Numbers or letters for each graph can be set by arg "graphs"

; This script is written in Ncl because Ngl does not support the needed transparent 
; shading between curves (at time of design)
  

; Usage example :

  ; ncl -Q zonal_means.ncl \
  ; 'title="Multi-model zonal mean long-term changes in P and P-E"' \
  ; 'files="out_ssp126_pr.nc out_ssp126_P-E.nc out_ssp245_pr.nc out_ssp245_P-E.nc out_ssp585_pr.nc out_ssp585_P-E.nc"' \
  ; 'nx=2' 'ny=3' \
  ; 'columns="Precipitation|Precipitation minus evaporation"' \
  ; 'lines="SSP1-2.6 (mm/day)|SSP2-4.5 (mm/day)|SSP5-8.5 (mm/day)"' \
  ; 'graphs="a)|b)|c)|d)|e)|f)"' \
  ; 'format="1200x1800"' \
  ; 'figfile="{figfile}"'

begin
;
; Read number of graphs in both directions and compute graph sizes
;  
  if (.not. isvar("nx")) then nx=1 end if
  if (.not. isvar("ny")) then ny=1 end if

  if (.not. isvar("files")) then
    print ("Must provide a blank separated list of filenames using arg 'files' ")
    status_exit(1)
  else
    filenames=str_split(files," ")
    d=dimsizes(filenames)
    if (( d .gt. nx*ny ) .or. ( d .lt. nx*(ny-1)+1 )) then
      print ("Mismatch between file list length and dimensions ")
      status_exit(1)
    end if
  end if

  if (.not. isvar("format")) then type="png" end if
  if (.not. isvar("type")) then type="png" end if
  
  if isvar("resolution") then
    if ( .not. ismissing(str_match(resolution,"x")) .or. .not. ismissing(str_match(resolution,"*")) ) then

      if .not. ismissing(str_match(resolution,"x")) then
        nb_pixels_or_inches = str_split(resolution, "x")
      else
        if .not. ismissing(str_match(resolution,"*")) then
          nb_pixels_or_inches = str_split(resolution, "*")
        end if
      end if
      width = stringtofloat(nb_pixels_or_inches(0))
      height = stringtofloat(nb_pixels_or_inches(1))
    
      if type .eq. "png" then ;image resolution in pixels
        type@wkWidth = width
        type@wkHeight = height
      else 
        if (type .eq. "pdf") .or. (type .eq. "eps") then ;image resolution in inches
          type@wkPaperWidthF  = width 
          type@wkPaperHeightF = height
        end if
      end if

    else ; resolution is not given by 'widthxheight' or 'width*height'
      
      if type .eq. "png" then 
        print("For PNG output, resolution must be given by 'widthxheight' or 'width*height'")
        status_exit(1)
      else
        if (type .eq. "pdf") .or. (type .eq. "eps") then
          type@wkPaperSize = resolution
        end if
      end if

    end if ; str_match
  end if ;resolution

  if isvar("columns") then
    column_titles=str_split(columns,"|")
    column_titles_height=0.021
  else
    column_titles_height=0.
  end if
  
  if isvar("lines") then
    line_titles=str_split(lines,"|")
    line_titles_width=0.014
  else
    line_titles_width=0.
  end if

  if isvar("graphs") then graph_titles=str_split(graphs,"|") end if

;
; Graphic code
;
  wks = gsn_open_wks(type,"zonal_means.png") ; send graphics to PNG file
  ;gsn_define_colormap(wks,cmap)

  if isvar("title") then 
    txres               = True                      ; text mods desired
    txres@txFontHeightF = 0.025                     ; text font height
    txres@txJust        = "TopCenter"              ; Default is "CenterCenter".
    gsn_text_ndc ( wks ,title, 0.5 ,0.98,txres)
  end if

  res = True

  res@gsnFrame           = False     ; Don't advance the frame
  title_height           = 0.08       ; general title
  interval               = 0.005      ; between graphs
  ;
  graph_height           = (1-title_height-column_titles_height-(ny+1)*interval)/int2flt(ny)
  xaxis_height           = 0.05      ; height of axis ticks + label
  res@vpHeightF          = graph_height - xaxis_height 
  ;
  graph_width            = (1-line_titles_width-(nx+1)*interval)/int2flt(nx)
  yaxis_width            = 0.08      ; width of axis ticks + label
  res@vpWidthF           = graph_width  - yaxis_width
;
; Title resources
;
  res@tiMainFontHeightF  = 0.015
  res@tiXAxisFontHeightF = 0.018
  res@tiYAxisFontHeightF = 0.018
  ;res@pmLegendDisplayMode = "Always"
;
  ;res@lgLegendOn	= True
  ;res@lgItemCount = 2
  ;res@lgItemOrder = (/1, 5/)

  ;res@lgMonoItemType = True
  ;res@xyLineThicknessF   = 3.0

  fact=24.*3600. ; convert kg m**-2 s-1 to mm day-1
  ;
  do iy=1,ny
    do ix=1,nx
      number=(iy-1)*nx+ix-1
      
      ; plot geometry
      res@vpXF              = interval + yaxis_width + (ix-1)*(graph_width+interval)    ; X,Y position of first plot
      res@vpYF              = 1-(title_height + xaxis_height + (iy-1)*(graph_height+interval))
      res@gsnYRefLine       = 0.
      res@gsnXRefLine       = 0.
      res@trYMinF           = -1.6 ; -1.6
      res@trYMaxF           = 2.8 ; 2.4
      if ((iy .eq. 1 ) .and. isvar("columns")) then
        res@tiMainString      = column_titles(ix-1)
      else
        delete(res@tiMainString)
      end if
      ;res@tiXAxisString     = "Latitude"
                                ;res@tiXAxisOn         = False
      res@tiYAxisFontHeightF  = 0.014
      if ((ix .eq. 1 ) .and. isvar("lines")) then
        res@tiYAxisString      = line_titles(iy-1)
      else
        delete(res@tiYAxisString)
        ;res@tiYAxisString     = "mm/day"
      end if
      transparency=0.2
      if (iy .eq. 1 ) then ; assuming it's SSP126
        ssp=(/ 30./256., 150./256.,  132./256., transparency /)
      else
        if (iy .eq. 2 ) then ; assuming it's SSP5245
          ssp=(/ 69./256., 118./256.,  191./256., transparency /)
        else
          if (iy .eq. 3 ) then ; assuming it's SSP5-8.5
            ssp=(/ 128./256., 54./256.,  168./256., transparency /)
          end if
        end if
      end if
      transparent=(/1.,1.,1.,0./)
      grey=(/0.,0.,0.,0.10/)
      res@xyMonoLineColor  = True
      sspf=ssp
      sspf(3)=1.
      res@xyLineColor      = sspf
      res@gsnXYFillColors   = (/ssp,ssp,transparent,grey,transparent/)
      res@xyMonoDashPattern = False
      res@xyDashPatterns    = (/ 0  , 0 , 0  , 0  , 0  , 11/)
      res@xyMonoLineThickness = False
      res@xyLineThicknesses = (/ 0.5, 5., 0.5, 0.5, 0.5, 3./)

      res@tmXTBorderOn      = False
      res@tmXTOn            = False
      res@tmXUseBottom      = False
      res@tmYRBorderOn      = False
      res@tmYROn            = False
      res@tmYUseLeft        = False

      res@tmXBLabelFontHeightF = 0.012 ;!
      res@tmYLLabelFontHeightF = 0.012 ;!

      res@tmYLMode = "Explicit"
      res@tmYLValues = (/ -1, 0 ,1,2 /)
      res@tmYLLabels = (/ "-1", "0" ,"1","2" /) 
       res@tmYLTickStartF  = -1.
      ;res.tmYLDataBottomF = -20.
      ;res.tmYLDataTopF    =  40.
      res@tmYLTickSpacingF=  1
      
      ; read data
      ff=filenames(number)
      f:=addfile(ff,"r")
      if .not. ismissing (str_match(ff,"P-E")) then
        varname="P-E"
      else
        if .not. ismissing (str_match(ff,"evspsbl")) then
          varname="evspsbl"
        else
          varname="pr"
        end if
      end if
      pctl5   =varname+"_pctl5"
      pctl95  =varname+"_pctl95"
      variab5 =varname+"_variab5"
      variab95=varname+"_variab95"
      mean=varname+"_mean"
      land_mean=varname+"_land_mean"
      
      fmean:=f->$mean$(0,:,0)
      nblat:=dimsizes(fmean)
      y:=new((/6,nblat/),float)
      y(0,:)=fact*f->$pctl5$(0,:,0)
      y(1,:)=fact*f->$mean$(0,:,0)
      y(2,:)=fact*f->$pctl95$(0,:,0)
      y(3,:)=fact*f->$variab5$(0,:,0)
      y(4,:)=fact*f->$variab95$(0,:,0)
      y(5,:)=fact*f->$land_mean$(0,:,0)
      
      plot = gsn_csm_xy(wks,f->lat,y,res)
      
      if isvar("graphs") then
        tires               = True                      ; text mods desired
        tires@txFontHeightF = 0.012                     ; text font height
        tires@txJust        = "TopLeft"              ; Default is "CenterCenter".
        gsn_text_ndc(wks,graph_titles(number),(res@vpXF)+0.01,(res@vpYF)-0.01,tires)
      end if

      if (iy .eq. 3 ) .and. (varname .eq. "pr")
        legres               = True                      
        legres@txFontHeightF = 0.012                    
        legres@txJust        = "CenterLeft"              
        gsn_text(wks,plot,"models mean ",31,2.,legres)
        gsn_polyline(wks,plot,(/3.,30./),(/0.8,2./),legres)

        gsn_text(wks,plot,"models mean, land",31,1.6,legres)
        gsn_polyline(wks,plot,(/12.0,30./),(/0.40,1.6/),legres)

        gsn_text(wks,plot,"[5%,95%] internal variability ",30.,-0.6,legres)
        gsn_polyline(wks,plot,(/5.,30./),(/-0.33,-0.6/),legres)

        gsn_text(wks,plot,"[5%,95%] across models ",30.,-1,legres)
        gsn_polyline(wks,plot,(/11.,30./),(/-1.05,-1/),legres)
      end if

      
    end do
  end do
  
  frame(wks)
  print("OK")
end
